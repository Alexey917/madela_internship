import asyncio

from sqlalchemy import select

from app.db import SessionLocal
from app.models import User, UserRole
from app.security import hash_password

SEED_USERS = [
    {"email": "admin@shop.local", "password": "admin123", "role": UserRole.ADMIN},
    {"email": "pvpuvk@yandex.ru", "password": "user123", "role": UserRole.USER},
]


async def seed() -> None:
    async with SessionLocal() as session:
        created = 0
        skipped = 0
        for item in SEED_USERS:
            existing = await session.execute(select(User).where(User.email == item["email"]))
            if existing.scalar_one_or_none() is not None:
                skipped += 1
                continue
            session.add(User(
                email=item["email"],
                hashed_password=hash_password(item["password"]),
                role=item["role"],
            ))
            created += 1
        await session.commit()
    print(f"✅ Auth seed: created={created}, skipped={skipped}")


if __name__ == "__main__":
    asyncio.run(seed())