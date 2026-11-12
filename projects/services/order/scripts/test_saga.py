import asyncio
from decimal import Decimal

from app.db import SessionLocal
from app.repository import OrderRepository
from app.saga import ServiceSaga


async def main() -> None:
    async with SessionLocal() as session:
        repo = OrderRepository(session)
        saga = ServiceSaga(session)

        # 1. Создать заказ
        order = await repo.create(
            user_id="user-saga-test",
            items=[
                {"product_id": 9, "quantity": 1, "unit_price": Decimal("12990.00")},
            ],
        )
        print(f"Created order id={order.id}, total={order.total_amount}")

        # 2. Запустить SAGA
        await saga.start(order.id)
        print("SAGA started — inventory.reserve published")

    # Проверь outbox
    # Проверь логи Inventory
    # Подожди, пока Inventory ответит

    await asyncio.sleep(3)

    async with SessionLocal() as session:
        repo = OrderRepository(session)
        order = await repo.get(order.id)
        print(f"Order status: {order.status}")


if __name__ == "__main__":
    asyncio.run(main())