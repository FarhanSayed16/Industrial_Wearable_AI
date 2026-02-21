"""
Industrial Wearable AI — FastAPI Dependencies
"""
from uuid import UUID

import os
from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ALGORITHM, SECRET_KEY
from app.database import get_db
from app.models import User
from app.redis_client import redis_client

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract JWT from Authorization header and return User. Raises 401 if invalid."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        jti = payload.get("jti")
        
        if not sub:
            raise HTTPException(status_code=401, detail="Invalid token")
            
        # Check if token is blacklisted in Redis
        if jti:
            is_blacklisted = await redis_client.exists(f"blacklist:{jti}")
            if is_blacklisted:
                raise HTTPException(status_code=401, detail="Token has been logged out")
                
        user_id = UUID(sub)
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_role(*allowed_roles: str):
    """
    Dependency factory: require user to have one of the allowed roles.
    Roles hierarchy: super_admin > factory_admin > supervisor > viewer
    Usage: Depends(require_role("super_admin", "factory_admin"))
    """
    ROLE_HIERARCHY = {
        "super_admin": 4,
        "factory_admin": 3,
        "supervisor": 2,
        "viewer": 1,
    }

    async def _check_role(user: User = Depends(get_current_user)) -> User:
        user_role = getattr(user, "role", "viewer") or "viewer"
        if user_role in allowed_roles:
            return user
        # Also allow higher roles (super_admin can do anything)
        user_level = ROLE_HIERARCHY.get(user_role, 0)
        min_required = min(ROLE_HIERARCHY.get(r, 99) for r in allowed_roles)
        if user_level >= min_required:
            return user
        raise HTTPException(
            status_code=403,
            detail=f"Insufficient permissions. Required: {', '.join(allowed_roles)}",
        )

    return _check_role

EDGE_API_KEY = os.getenv("EDGE_API_KEY", "dev-edge-key-123")

def verify_edge_api_key(x_api_key: str = Header(None)):
    """Authenticate Edge Gateway requests using a static API key."""
    if not x_api_key or x_api_key != EDGE_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing Edge API Key")

