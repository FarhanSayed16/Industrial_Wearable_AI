"""
Industrial Wearable AI — Auth API
POST /api/auth/login, POST /api/auth/register, POST /api/auth/change-password, GET /api/auth/me
"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from jose import JWTError, jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.redis_client import redis_client

router = APIRouter(prefix="/api", tags=["auth"])
ph = PasswordHasher()

def _hash_password(password: str) -> str:
    return ph.hash(password)


def _verify_password(plain: str, hashed: str) -> bool:
    try:
        if hashed.startswith("$2b$"):
            # Fallback for old bcrypt hashes created before Phase 7
            import bcrypt
            return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
        return ph.verify(hashed, plain)
    except VerifyMismatchError:
        return False


def _create_access_token(subject: str) -> str:
    jti = uuid.uuid4().hex
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": subject, "exp": expire, "jti": jti}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/auth/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Accept username/password; verify with bcrypt; return JWT."""
    stmt = select(User).where(User.username == data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user or not _verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = _create_access_token(str(user.id))
    return TokenResponse(access_token=token)


@router.post("/auth/register", response_model=TokenResponse)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Create new user; return JWT on success."""
    stmt = select(User).where(User.username == data.username)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed = _hash_password(data.password)
    user = User(username=data.username, hashed_password=hashed)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = _create_access_token(str(user.id))
    return TokenResponse(access_token=token)


@router.post("/auth/change-password")
async def change_password(
    data: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change password for authenticated user."""
    if not _verify_password(data.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.hashed_password = _hash_password(data.new_password)
    await db.commit()
    return {"message": "Password updated successfully"}


@router.get("/auth/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """Return current authenticated user."""
    return UserResponse(id=str(user.id), username=user.username)


@router.post("/auth/logout")
async def logout(request: Request, user: User = Depends(get_current_user)):
    """Add the user's current JWT to the Redis blacklist."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Missing or invalid token")
        
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        exp = payload.get("exp")
        
        if jti and exp:
            # Calculate TTL for the key in Redis (time until token naturally expires)
            now = int(datetime.now(timezone.utc).timestamp())
            ttl = max(0, exp - now)
            if ttl > 0:
                await redis_client.setex(f"blacklist:{jti}", ttl, "blacklisted")
    except JWTError:
        pass # If token is invalid anyway, no need to blacklist
        
    return {"message": "Logged out successfully"}
