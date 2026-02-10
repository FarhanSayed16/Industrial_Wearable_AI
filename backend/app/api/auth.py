"""
Industrial Wearable AI — Auth API
POST /api/auth/login, POST /api/auth/register, POST /api/auth/change-password, GET /api/auth/me
"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError, jwt
import bcrypt
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

router = APIRouter(prefix="/api", tags=["auth"])


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def _create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": subject, "exp": expire}
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
