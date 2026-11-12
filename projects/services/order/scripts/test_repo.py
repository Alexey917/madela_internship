import asyncio
from decimal import Decimal

from app.db import SessionLocal
from app.models import OrderStatus, SagaStatus
from app.repository import OrderRepository


async def main() -> None:
    async with SessionLocal() as session:
        repo = OrderRepository(session)

        order = await repo.create(
            user_id="user-1",
            items=[
                {"product_id": 9, "quantity": 1, "unit_price": Decimal("12990.00")},
                {"product_id": 1, "quantity": 2, "unit_price": Decimal("2990.00")},
            ],
        )
        print(f"Created order id={order.id}, total={order.total_amount}, status={order.status}")
        print(f"Items: {[(i.product_id, i.quantity, i.unit_price) for i in order.items]}")

        fetched = await repo.get(order.id)
        print(f"Fetched: id={fetched.id}, total={fetched.total_amount}, items={len(fetched.items)}")

        await repo.update_status(order.id, OrderStatus.RESERVED)
        await repo.update_saga_status(order.id, SagaStatus.RESERVED)
        print(f"Updated to RESERVED")

        await repo.update_status(order.id, OrderStatus.FAILED)
        await repo.update_saga_status(order.id, SagaStatus.COMPENSATING, last_error="payment_failed")
        print(f"Updated to FAILED/COMPENSATING")

        saga_updated = await repo.update_saga_status(order.id, SagaStatus.CANCELLED)
        await repo.update_status(order.id, OrderStatus.CANCELLED)
        print(f"Saga last_error: {saga_updated.last_error}")

        orders = await repo.list_by_user("user-1")
        print(f"User orders: {len(orders)}")


if __name__ == "__main__":
    asyncio.run(main())