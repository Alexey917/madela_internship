import asyncio
from decimal import Decimal

from app.db import SessionLocal
from app.repository import ProductRepository


async def main() -> None:
    async with SessionLocal() as session:
        repo = ProductRepository(session)

        # create
        product = await repo.create(
            name="Каркассон",
            price=Decimal("2990.00"),
            stock=15,
            description="Базовая игра",
            publisher="Hobby World",
            min_players=2,
            max_players=5,
            play_time_minutes=45,
            min_age=8,
        )
        print(f"Created: id={product.id}, name={product.name}, price={product.price}")

        # get
        fetched = await repo.get(product.id)
        print(f"Fetched: {fetched.name}, price={fetched.price}")

        # update
        updated = await repo.update(stock=10, product_id=product.id, price=Decimal("2790.00"))
        print(f"Updated: stock={updated.stock}, price={updated.price}")

        # list
        products, total = await repo.list(page=1, size=10)
        print(f"List: total={total}, items={[p.name for p in products]}")

        # soft-delete
        await repo.update(product.id, stock=10, price=Decimal("4790.00"), is_active=False)
        hidden = await repo.get(product.id)
        print(f"After soft-delete: {hidden}")  # None
        visible_in_list, total_after = await repo.list()
        print(f"List after soft-delete: total={total_after}")


if __name__ == "__main__":
    asyncio.run(main())