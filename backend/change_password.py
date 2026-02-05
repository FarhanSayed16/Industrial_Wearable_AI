"""
Industrial Wearable AI — Change Admin Password
Run: python change_password.py (from backend/)
Usage: python change_password.py admin newpassword
       python change_password.py admin  (prompts for new password)
"""
import asyncio
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bcrypt
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import User


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


async def change_password(username: str, new_password: str):
    async with AsyncSessionLocal() as db:
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            print(f"User '{username}' not found.")
            return False
        user.hashed_password = _hash_password(new_password)
        await db.commit()
        print(f"Password updated for user '{username}'.")
        return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python change_password.py <username> [new_password]")
        sys.exit(1)
    username = sys.argv[1]
    if len(sys.argv) >= 3:
        new_password = sys.argv[2]
    else:
        new_password = getpass.getpass("New password: ")
        confirm = getpass.getpass("Confirm password: ")
        if new_password != confirm:
            print("Passwords do not match.")
            sys.exit(1)
    if len(new_password) < 6:
        print("Password must be at least 6 characters.")
        sys.exit(1)
    success = asyncio.run(change_password(username, new_password))
    sys.exit(0 if success else 1)
