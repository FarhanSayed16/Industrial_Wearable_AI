"""
Industrial Wearable AI — System Config API
Manage global configurable thresholds (Admin only).
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_role
from app.models import SystemConfig, User
from app.services.audit import log_action

# require admin role for full config access
router = APIRouter(prefix="/api/config", tags=["config"])


class ConfigItem(BaseModel):
    key: str
    value: str
    description: str | None = None

    class Config:
        from_attributes = True


@router.get("", response_model=List[ConfigItem])
async def get_all_config(
    user: User = Depends(require_role("super_admin", "factory_admin", "supervisor")),
    db: AsyncSession = Depends(get_db),
):
    """Get all configuration variables."""
    stmt = select(SystemConfig).order_by(SystemConfig.key)
    result = await db.execute(stmt)
    configs = result.scalars().all()
    return configs


@router.post("", response_model=ConfigItem)
async def set_config(
    item: ConfigItem,
    user: User = Depends(require_role("super_admin", "factory_admin")),
    db: AsyncSession = Depends(get_db),
):
    """Set or create a configuration variable."""
    stmt = select(SystemConfig).where(SystemConfig.key == item.key)
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    
    if config:
        config.value = item.value
        if item.description is not None:
            config.description = item.description
    else:
        config = SystemConfig(key=item.key, value=item.value, description=item.description)
        db.add(config)
        
    await db.commit()
    await db.refresh(config)
    
    # Audit log
    await log_action(db, "update_config", f"config:{item.key}", f"Set value to {item.value}", user)
    
    return config
