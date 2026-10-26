import asyncio

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Stock


SEED_STOCK = [
    {"product_id": 1, "available": 15},   # Каркассон
    {"product_id": 2, "available": 20},   # Catan
    {"product_id": 3, "available": 50},   # Манчкин
    {"product_id": 4, "available": 30},   # Codenames
    {"product_id": 5, "available": 10},   # Билет на поезд
    {"product_id": 6, "available": 25},   # Диксит
    {"product_id": 7, "available": 12},   # 7 Wonders
    {"product_id": 8, "available": 18},   # Splendor
    {"product_id": 9, "available": 3},    # Gloomhaven
    {"product_id": 10, "available": 8},   # Azul
    {"product_id": 11, "available": 14},   # Смертельные материалы
    {"product_id": 12, "available": 7},   # Морской бой
]


async def seed() -> None:
    async with SessionLocal() as session:
        created = 0
        skipped = 0
        for item in SEED_STOCK:
            existing = await session.execute(
                select(Stock).where(Stock.product_id == item["product_id"])
            )
            if existing.scalar_one_or_none() is not None:
                skipped += 1
                continue
            session.add(Stock(**item))
            created += 1
        await session.commit()
    print(f"✅ Inventory seed done: created={created}, skipped={skipped}")


if __name__ == "__main__":
    asyncio.run(seed())
