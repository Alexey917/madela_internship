import logging, json
from aio_pika import ExchangeType

from app.broker import broker
from app.db import SessionLocal
from app.saga import SagaService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_inventory_consumer() -> None:
    """Слушает ответы от Inventory."""
    if broker._channel is None:
        raise RuntimeError("Broker is not connected")

    exchange = await broker._channel.declare_exchange(
        "inventory.events", ExchangeType.TOPIC, durable=True
    )

    queue = await broker._channel.declare_queue("order.inventory-events", durable=True)
    await queue.bind(exchange, routing_key="inventory.reserved")
    await queue.bind(exchange, routing_key="inventory.failed")
    await queue.bind(exchange, routing_key="inventory.released")

    logger.info("Order inventory consumer started: queue=%s", queue.name)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    payload = json.loads(message.body)
                    await _handle_inventory_event(message.routing_key, payload)
                except Exception:
                    logger.exception("Failed to process inventory event")


async def start_payment_consumer() -> None:
    """Слушает ответы от Payment."""
    if broker._channel is None:
        raise RuntimeError("Broker is not connected")
    
    exchange = await broker._channel.declare_exchange(
        "payment.events", ExchangeType.TOPIC, durable=True
    )
    
    queue = await broker._channel.declare_queue("order.inventory-events", durable=True)
    await queue.bind(exchange, routing_key="payment.succeeded")
    await queue.bind(exchange, routing_key="payment.failed")
    await queue.bind(exchange, routing_key="payment.refunded")
    
    logger.info("Order payment consumer started: queue=%s", queue.name)
    
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    payload = json.loads(message.body)
                    await _handle_payment_event(message.routing_key, payload)
                except Exception:
                    logger.exception("Failed to process payment event")


async def _handle_inventory_event(routing_key: str, payload: dict) -> None:
    order_id = payload.get("order_id")
    if not order_id:
        logger.warning("Missing order_id in %s: %s", routing_key, payload)
        return

    logger.info("Received %s for order_id=%s", routing_key, order_id)

    async with SessionLocal() as session:
        saga = SagaService(session)

        if routing_key == "inventory.reserved":
            await saga.on_inventory_reserved(order_id)
        elif routing_key == "inventory.failed":
            await saga.on_inventory_failed(order_id, payload.get("reason"))
        elif routing_key == "inventory.released":
            await saga.on_inventory_released(order_id)


async def _handle_payment_event(routing_key: str, payload: dict) -> None:
    order_id = payload.get("order_id")
    if not order_id:
        logger.warning("Missing order_id in %s: %s", routing_key, payload)
        return

    logger.info("Received %s for order_id=%s", routing_key, order_id)

    async with SessionLocal() as session:
        saga = SagaService(session)

        if routing_key == "payment.succeeded":
            await saga.on_payment_succeeded(order_id)
        elif routing_key == "payment.failed":
            await saga.on_payment_failed(order_id, payload.get("reason"))
        elif routing_key == "payment.refunded":
            await saga.on_payment_refunded(order_id)