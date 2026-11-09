import asyncio
from passlib.context import CryptContext
from sqlalchemy import select

from app.db import SessionLocal
from app.models import User, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SEED_USERS = [
    {"email": "admin@shop.local", "password": "admin123", "role": UserRole.ADMIN},
    {"email": "user@shop.local", "password": "user123", "role": UserRole.USER},
]


async def seed() -> None:
    async with SessionLocal() as session:
        created = 0
        for item in SEED_USERS:
            existing = await session.execute(select(User).where(User.email == item["email"]))
            if existing.scalar_one_or_none():
                continue
            session.add(User(
                email=item["email"],
                hashed_password=pwd_context.hash(item["password"]),
                role=item["role"],
            ))
            created += 1
        await session.commit()
    print(f"✅ Auth seed: created={created}")


if __name__ == "__main__":
    asyncio.run(seed())