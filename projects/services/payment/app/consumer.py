import json, logging

from aio_pika import ExchangeType

from app.broker import broker
from app.db import SessionLocal
from app.repository import PaymentRepository
from app.models import PaymentStatus


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
    await queue.bind(exchange, routing_key="payment.refund")

    logger.info("Payment consumer started: queue=%s, routing_key=%s", QUEUE_NAME, ROUTING_KEY)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    payload = json.loads(message.body)
                    if message.routing_key == "payment.process":
                        await _handle_payment_process(payload)
                    elif message.routing_key == "payment.refund":
                        await _handle_payment_refund(payload)
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


async def _handle_payment_refund(payload: dict) -> None:
    order_id = payload.get("order_id")
    if not order_id:
        return
    async with SessionLocal() as session:
        repo = PaymentRepository(session)
        payment = await repo.get_by_order_id(order_id)
        if payment is None:
            logger.warning("Refund: payment for order %s not found", order_id)
            return
        if payment.status != PaymentStatus.SUCCEEDED:
            logger.info("Refund: payment %s not succeeded, skip", payment.id)
            return
        await repo.refund(payment.id, reason="order_cancelled")
        # repo.refund сам публикует payment.refunded 
    logger.info("Refunded payment for order_id=%s", order_id)