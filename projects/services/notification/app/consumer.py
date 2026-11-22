import json
import logging

from aio_pika import ExchangeType

from app.broker import broker
from app.db import SessionLocal
from app.email import send_email
from app.repository import NotificationRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


EMAIL_EVENTS = {"order.completed", "order.cancelled"}

SUBJECTS = {
    "order.completed": "Ваш заказ оплачен",
    "order.cancelled": "Ваш заказ отменён",
}


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

    user_email = payload.get("user_email")
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

    # Отправляем email только для финальных событий и только при создании новой записи
    if event_type in EMAIL_EVENTS and user_email:
        subject = SUBJECTS.get(event_type, "Board Games Shop")
        await send_email(user_email, subject, message_text)
    elif event_type in EMAIL_EVENTS and not user_email:
        logger.warning(
            "No user_email for %s order_id=%s — email skipped",
            event_type, order_id,
        )


def _format_message(event_type: str, order_id: int | str) -> str:
    templates = {
        "order.completed": (
            f"Здравствуйте!\n\n"
            f"Ваш заказ #{order_id} оплачен и готов к отправке.\n\n"
            f"Спасибо, что выбрали Board Games Shop!\n"
            f"🎲"
        ),
        "order.cancelled": (
            f"Здравствуйте!\n\n"
            f"К сожалению, ваш заказ #{order_id} отменён.\n"
            f"Средства не были списаны.\n\n"
            f"Если вы оплачивали картой — деньги вернутся в течение 3-5 рабочих дней.\n\n"
            f"Board Games Shop"
        ),
        "payment.succeeded": f"Оплата заказа #{order_id} прошла успешно.",
        "payment.failed": f"Оплата заказа #{order_id} не прошла.",
    }
    return templates.get(event_type, f"Событие {event_type} по заказу #{order_id}")