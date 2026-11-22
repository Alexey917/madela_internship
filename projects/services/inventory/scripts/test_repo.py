import asyncio

from app.db import SessionLocal
from app.repository import StockRepository


async def main() -> None:
    async with SessionLocal() as session:
        repo = StockRepository(session)

        # get
        stock = await repo.get(9)   # Gloomhaven
        print(f"Initial: available={stock.available}, reserved={stock.reserved}")

        # reserve 1
        result = await repo.reserve(9, 1)
        print(f"After reserve(1): available={result.available}, reserved={result.reserved}")

        # reserve больше, чем есть
        fail = await repo.reserve(9, 100)
        print(f"Reserve(100) failed: {fail}")   # None

        # release (компенсация)
        result = await repo.release(9, 1)
        print(f"After release(1): available={result.available}, reserved={result.reserved}")

        # reserve снова
        result = await repo.reserve(9, 1)
        print(f"After reserve(1) again: available={result.available}, reserved={result.reserved}")

        # commit (списание после оплаты)
        result = await repo.commit(9, 1)
        print(f"After commit(1): available={result.available}, reserved={result.reserved}")


if __name__ == "__main__":
    asyncio.run(main())