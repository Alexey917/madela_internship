import json
import logging

from aio_pika import ExchangeType

from app.broker import broker
from app.db import SessionLocal
from app.repository import NotificationRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start_order_events_consumer() -> None:
    """Слушает order.completed / order.cancelled."""
    if broker._channel is None:
        raise RuntimeError("Broker is not connected")

    exchange = await broker._channel.declare_exchange(
        "order.events", ExchangeType.TOPIC, durable=True
    )
    queue = await broker._channel.declare_queue("notification.order-events", durable=True)
    await queue.bind(exchange, routing_key="order.completed")
    await queue.bind(exchange, routing_key="order.cancelled")

    logger.info("Notification order consumer started: queue=%s", queue.name)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    payload = json.loads(message.body)
                    await _handle_event(message.routing_key, payload)
                except Exception:
                    logger.exception("Failed to process order event")


async def start_payment_events_consumer() -> None:
    """Слушает payment.succeeded / payment.failed."""
    if broker._channel is None:
        raise RuntimeError("Broker is not connected")

    exchange = await broker._channel.declare_exchange(
        "payment.events", ExchangeType.TOPIC, durable=True
    )
    queue = await broker._channel.declare_queue("notification.payment-events", durable=True)
    await queue.bind(exchange, routing_key="payment.succeeded")
    await queue.bind(exchange, routing_key="payment.failed")

    logger.info("Notification payment consumer started: queue=%s", queue.name)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    payload = json.loads(message.body)
                    await _handle_event(message.routing_key, payload)
                except Exception:
                    logger.exception("Failed to process payment event")


async def _handle_event(event_type: str, payload: dict) -> None:
    order_id = payload.get("order_id")
    if not order_id:
        logger.warning("Missing order_id in %s: %s", event_type, payload)
        return

    message_text = _format_message(event_type, order_id)
    logger.info("[NOTIFICATION] %s | order_id=%s | %s", event_type, order_id, message_text)

    async with SessionLocal() as session:
        repo = NotificationRepository(session)
        created = await repo.create_notification(
            event_type=event_type,
            order_id=int(order_id),
            message=message_text,
        )

    if created is not None:
        logger.info("[NOTIFICATION] %s | order_id=%s | %s", event_type, order_id, message_text)
    else:
        logger.info("[NOTIFICATION] %s | order_id=%s | duplicate, skipped", event_type, order_id)


def _format_message(event_type: str, order_id: int | str) -> str:
    templates = {
        "order.completed": f"Ваш заказ #{order_id} оплачен и готов к отправке.",
        "order.cancelled": f"Заказ #{order_id} отменён. Средства не списаны.",
        "payment.succeeded": f"Оплата заказа #{order_id} прошла успешно.",
        "payment.failed": f"Оплата заказа #{order_id} не прошла. Попробуйте другой способ.",
    }
    return templates.get(event_type, f"Событие {event_type} по заказу #{order_id}")