"""
Industrial Wearable AI — Seed Default Admin User
Run: python seed_user.py (from backend/)
"""
import asyncio
import sys
from pathlib import Path

# Ensure backend is on path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import bcrypt
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import User


def _hash_password(password: str) -> str:
    """Hash password with bcrypt (compatible with passlib verify)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


async def seed_admin():
    async with AsyncSessionLocal() as db:
        stmt = select(User).where(User.username == "admin")
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            if existing.role != "super_admin":
                existing.role = "super_admin"
                await db.commit()
                print("Upgraded existing admin user to super_admin role.")
            else:
                print("Admin user already exists and is super_admin.")
            return

        hashed = _hash_password("admin123")
        user = User(username="admin", hashed_password=hashed, role="super_admin")
        db.add(user)
        await db.commit()
        print("Created admin user (username=admin, password=admin123, role=super_admin)")


if __name__ == "__main__":
    asyncio.run(seed_admin())
