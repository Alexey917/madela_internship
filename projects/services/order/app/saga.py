import logging
from decimal import Decimal 

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import OrderStatus, SagaStatus
from app.outbox import enqueue_event
from app.repository import OrderRepository


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServiceSaga:
    """
    Оркестратор SAGA.
    Все методы идемпотентны: повторный вызов с теми же данными — no-op,
    если состояние уже соответствует.
    """
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = OrderRepository(session)

    async def start(self, order_id: int, items: list[dict]) -> None:
        """Запускает SAGA: публикует inventory.reserve."""
        order = await self.repo.get(order_id)
        if order is None:
            logger.warning("SAGA start: order %s not found", order_id)
            return

        await enqueue_event(
            self.session,
            event_type="inventory.reserve",
            payload={
                "order_id": order_id,
                "items": [
                    {"product_id": i.product_id, "quantity": i.quantity}
                    for i in order.items
                ],
            },
        )
        await self.session.commit()
        logger.info("SAGA started: order_id=%s, published inventory.reserve", order_id)

    async def on_inventory_reserved(self, order_id: int) -> None:
        """Получен inventory.reserved → публикуем payment.process."""
        order = await self.repo.get(order_id)
        if order is None:
            logger.warning("on_inventory_reserved: order %s not found", order_id)
            return

        if order.status not in (OrderStatus.PENDING, OrderStatus.RESERVED):
            logger.info(
                "on_inventory_reserved: order %s in status %s — skip",
                order_id, order.status,
            )
            return

        await self.repo.update_status(order_id, OrderStatus.RESERVED)
        await self.repo.update_saga_status(order_id, SagaStatus.RESERVED)

        await enqueue_event(
            self.session,
            event_type="payment.process",
            payload={
                "order_id": order_id,
                "amount": str(order.total_amount),
            },
        )
        await self.session.commit()
        logger.info("SAGA: order_id=%s → RESERVED, published payment.process", order_id)


    async def on_inventory_failed(self, order_id: int, reason: str | None = None) -> None:
        """Получен inventory.failed → сразу компенсация (Payment не вызывался)."""
        order = await self.repo.get(order_id)
        if order is None:
            logger.warning("on_inventory_failed: order %s not found", order_id)
            return

        if order.status in (OrderStatus.CANCELLED, OrderStatus.COMPLETED):
            logger.info(
                "on_inventory_failed: order %s already %s — skip",
                order_id, order.status,
            )
            return

        await self.repo.update_saga_status(
            order_id, SagaStatus.COMPENSATING, last_error=reason or "inventory_failed"
        )
        await self.repo.update_status(order_id, OrderStatus.FAILED)

        # Payment ещё не вызывался — компенсировать нечего
        await self.repo.update_saga_status(
            order_id, SagaStatus.CANCELLED, last_error=reason or "inventory_failed"
        )
        await self.repo.update_status(order_id, OrderStatus.CANCELLED)
        await self.session.commit()
        logger.info("SAGA: order_id=%s → CANCELLED (inventory failed)", order_id)


    async def on_payment_succeeded(self, order_id: int) -> None:
        """Получен payment.succeeded → публикуем inventory.commit → COMPLETED."""
        order = await self.repo.get(order_id)
        if order is None:
            logger.warning("on_payment_succeeded: order %s not found", order_id)
            return

        if order.status in (OrderStatus.COMPLETED, OrderStatus.CANCELLED):
            logger.info(
                "on_payment_succeeded: order %s already %s — skip",
                order_id, order.status,
            )
            return

        await self.repo.update_status(order_id, OrderStatus.PAID)
        await self.repo.update_saga_status(order_id, SagaStatus.PAID)

        # Финализируем резерв — публикуем inventory.commit
        await enqueue_event(
            self.session,
            event_type="inventory.commit",
            payload={
                "order_id": order_id,
                "items": [
                    {"product_id": i.product_id, "quantity": i.quantity}
                    for i in order.items
                ],
            },
        )

        await self.repo.update_status(order_id, OrderStatus.COMPLETED)
        await self.repo.update_saga_status(order_id, SagaStatus.COMPLETED)
        await self.session.commit()
        logger.info("SAGA: order_id=%s → COMPLETED", order_id)


    async def on_payment_failed(self, order_id: int, reason: str | None = None) -> None:
        """Получен payment.failed → компенсация (release)."""
        order = await self.repo.get(order_id)
        if order is None:
            logger.warning("on_payment_failed: order %s not found", order_id)
            return

        if order.status in (OrderStatus.CANCELLED, OrderStatus.COMPLETED):
            logger.info(
                "on_payment_failed: order %s already %s — skip",
                order_id, order.status,
            )
            return

        await self.repo.update_saga_status(
            order_id, SagaStatus.COMPENSATING, last_error=reason or "payment_failed"
        )
        await self.repo.update_status(order_id, OrderStatus.FAILED)

        # Компенсация: вернуть резерв
        await enqueue_event(
            self.session,
            event_type="inventory.release",
            payload={
                "order_id": order_id,
                "items": [
                    {"product_id": i.product_id, "quantity": i.quantity}
                    for i in order.items
                ],
            },
        )
        await self.session.commit()
        logger.info(
            "SAGA: order_id=%s → COMPENSATING (payment failed), published inventory.release",
            order_id,
        )


    async def on_inventory_released(self, order_id: int) -> None:
        """Получен inventory.released → CANCELLED."""
        order = await self.repo.get(order_id)
        if order is None:
            return

        if order.status == OrderStatus.CANCELLED:
            return

        await self.repo.update_status(order_id, OrderStatus.CANCELLED)
        await self.repo.update_saga_status(order_id, SagaStatus.CANCELLED)
        await self.session.commit()
        logger.info("SAGA: order_id=%s → CANCELLED (released)", order_id)


    async def cancel(self, order_id: int) -> None:
        """Ручная отмена заказа. Только для PENDING / RESERVED."""
        order = await self.repo.get(order_id)
        if order is None:
            raise ValueError("Order not found")

        if order.status in (OrderStatus.COMPLETED, OrderStatus.CANCELLED):
            raise ValueError(f"Cannot cancel order in status {order.status}")

        if order.status == OrderStatus.PAID:
            await enqueue_event(
                self.session,
                event_type="payment.refund",
                payload={"order_id": order_id},
            )
            await self.repo.update_saga_status(order_id, SagaStatus.COMPENSATING, last_error="cancelled_by_user")
            await self.repo.update_status(order_id, OrderStatus.FAILED)
            await self.session.commit()
            logger.info("SAGA: order_id=%s → COMPENSATING (cancel PAID), published payment.refund", order_id)
            return

        # Если PENDING — Inventory мог ещё не ответить. Публикуем release —
        # если резерва нет, Inventory вернёт 409 (игнорируем).
        await self.repo.update_saga_status(
            order_id, SagaStatus.COMPENSATING, last_error="cancelled_by_user"
        )
        await self.repo.update_status(order_id, OrderStatus.FAILED)

        await enqueue_event(
            self.session,
            event_type="inventory.release",
            payload={
                "order_id": order_id,
                "items": [
                    {"product_id": i.product_id, "quantity": i.quantity}
                    for i in order.items
                ],
            },
        )
        await self.session.commit()
        logger.info("SAGA: order_id=%s → COMPENSATING (user cancel)", order_id)


    async def on_payment_refunded(self, order_id: int) -> None:
        """Получен payment.refunded → публикуем inventory.release (если ещё не) → CANCELLED."""
        order = await self.repo.get(order_id)
        if order is None:
            return
        if order.status == OrderStatus.CANCELLED:
            return

        # Если inventory.release ещё не публиковался (отмена PAID-заказа) — публикуем
        # (если уже публиковался — Inventory обработает повторно, no-op)
        await enqueue_event(
            self.session,
            event_type="inventory.release",
            payload={
                "order_id": order_id,
                "items": [
                    {"product_id": i.product_id, "quantity": i.quantity}
                    for i in order.items
                ],
            },
        )
        await self.session.commit()
        logger.info("SAGA: order_id=%s → refunded, published inventory.release", order_id)
