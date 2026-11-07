from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Order, OrderStatus, OrderItem, SagaState, SagaStatus


class OrderRepository:
    def __init__(self, session: AsyncSession)  -> None:
        self.session = session

    async def get(self, order_id: int) -> Order | None:
        order = await self.session.execute(select(Order).where(Order.id == order_id))
        return order.scalar_one_or_none()

    async def create(self, user_id: str, items: list[dict]) -> Order:
        """
        Создаёт заказ с items и saga_state.
        items: [{"product_id": int, "quantity": int, "unit_price": Decimal}]
        """

        total = sum(i["unit_price"] * i["quantity"] for i in items)

        order = Order(
            user_id=user_id,
            status=OrderStatus.PENDING,
            total_amount=total,
        )

        self.session.add(order)
        await self.session.flush()

        for item in items:
            self.session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"]
                )
            )

        self.session.add(SagaState(order_id=order.id, status=SagaStatus.PENDING))

        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def update_status(self, order_id: int, status: OrderStatus) -> Order | None:
        order = await self.get(order_id)

        if order is None:
            return None

        order.status = status
        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def update_saga_status(
        self, 
        order_id: int, 
        saga_status: SagaStatus,
        last_error: str | None=None
    ) -> SagaState | None:
        result = self.session.execute(select(SagaState).where(SagaState.order_id == order_id))

        saga = result.scalar_one_or_none()

        if saga is None:
            return None

        saga.status = saga_status

        if last_error is not None:
            saga.last_error = last_error

        await self.session.commit()
        await self.session.refresh(saga)
        return saga

    async def list_by_user(self, user_id: str) -> list[Order]:
        result = await self.session.execute(
            select(Order).where(Order.user_id == user_id).order_by(Order.id.desc())
        )
        return list(result.scalars().all())

        





        

        