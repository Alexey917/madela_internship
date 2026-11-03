import json, logging

from aio_pika import ExchangeType

from app.broker import broker
from app.db import SessionLocal
from app.repository import PaymentRepository


logger = logging.getLogger(__name__)

EXCHANGE_NAME = "order.events"
QUEUE_NAME = "payment.order-events"
ROUTING_KEY = "payment.process"


async def start_consumer() -> None:
    """Слушает payment.process, создаёт Payment и вызывает шлюз."""
    if broker._channel is None:
        raise RuntimeError("Broker is not connected")

    exchange = await broker._channel.declare_exchange(
        EXCHANGE_NAME,
        ExchangeType.TOPIC,
        durable=True,
    )

    queue = await broker._channel.declare_queue(QUEUE_NAME, durable=True)
    await queue.bind(exchange, routing_key=ROUTING_KEY)

    logger.info("Payment consumer started: queue=%s, routing_key=%s", QUEUE_NAME, ROUTING_KEY)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    payload = json.loads(message.body)
                    await _handle_payment_process(payload)
                except Exception:
                    logger.exception("Failed to process payment.process")


async def _handle_payment_process(payload: dict) -> None:
    order_id = payload.get("order_id")
    amount = payload.get("amount")

    if not order_id or amount is None:
        logger.warning("Invalid payment.process payload: %s", payload)
        return

    logger.info("Processing payment.process: order_id=%s, amount=%s", order_id, amount)

    async with SessionLocal() as session:
        repo = PaymentRepository(session)
        payment = await repo.create_and_charge(order_id, amount)

    logger.info(
        "Payment processed: order_id=%s, payment_id=%s, status=%s",
        order_id, payment.id, payment.status,
    )