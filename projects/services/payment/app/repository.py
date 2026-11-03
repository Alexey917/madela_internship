from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal

from app.gateway_client import GatewayResponse, charge_with_retry
from app.models import Payment, PaymentStatus

class PaymentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, payment_id: int) -> Payment | None:
        payment = await self.session.execute(select(Payment).where(Payment.id == payment_id))
        return payment.scalar_one_or_none()


    async def get_by_order_id(self, order_id: str) -> Payment | None:
        payment = await self.session.execute(select(Payment).where(Payment.id == order_id))
        return payment.scalar_one_or_none()


    async def create_and_charge(self, order_id: str, amount: Decimal) -> Payment:
        """
        Создаёт Payment, вызывает шлюз, обновляет статус.
        Идемпотентно: если платёж по order_id уже есть — возвращает его.
        """
        existing = await self.session.get_by_order_id(order_id)

        if existing is not None:
            return existing

        payment = Payment(
            order_id = order_id,
            amount = amount,
            payment_status = PaymentStatus.PENDING
        )

        self.session.add(payment)
        await self.session.flush()

        try:
            gateway_response: GatewayResponse = await charge_with_retry(order_id, amount)
        except Exception as exc:
            payment.status = PaymentStatus.FAILED
            payment.failure_reason = f"gateway_error: {type(exc).__name__}"
            await self.session.commit()
            await self.session.refresh(payment)
            return payment

        payment.external_id = gateway_response.external_id
        if gateway_response.status == 'succeeded':
            payment.status = PaymentStatus.SUCCEEDED
        else:
            payment.status = PaymentStatus.FAILED
            payment.failure_reason = gateway_response.failure_reason

        await self.session.commit()
        await self.session.refresh(payment)
        return payment


    async def refund(self, payment_id: int, reason: str | None) -> Payment | None:
        """Возврат. Только для succeeded."""
        payment = await self.get(payment_id)
        if payment is None:
            return None
        if payment.status != PaymentStatus.SUCCEEDED:
            return None

        payment.status = PaymentStatus.REFUNDED
        if reason:
            payment.failure_reason = f"refund: {reason}"

        await self.session.commit()
        await self.session.refresh(payment)
        return payment

        