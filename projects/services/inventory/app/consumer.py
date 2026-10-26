import json
import logging

import aio_pika
from aio_pika import ExchangeType

from app.broker import broker
from app.db import SessionLocal
from app.repository import StockRepository

EXCHANGE_NAME = "order.events"
QUEUE_NAME = "inventory.order-events"
ROUTING_KEY = "order.created"

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

async def start_consumer() -> None:
    """Слушает order.created, резервирует товары."""
    if broker._channel is None:
        raise RuntimeError("Broker is not connected")

    exchange = await broker._channel.declare_exchange(
        EXCHANGE_NAME,
        ExchangeType.TOPIC,
        durable = True
    )

    queue = await broker._channel.declare_queue(QUEUE_NAME, durable = True)
    await queue.bind(exchange, ROUTING_KEY)

    logger.info("Inventory consumer started: queue=%s, routing_key=%s", QUEUE_NAME, ROUTING_KEY)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    payload = json.loads(message.body)
                    await _handle_order_created(payload)
                except Exception:
                    logger.exception("Failed to process order.created")


async def _handle_order_created(payload: dict) -> None:
    order_id = payload.get("order_id")
    items = payload.get("items", [])

    if not order_id or not items:
        logger.warning("Invalid order.created payload: %s", payload)
        return

    logger.info("Processing order.created: order_id=%s, items=%d", order_id, len(items))

    reserved: list[dict] = []

    async with SessionLocal() as session:
        repo = StockRepository(session)

        for item in items:
            product_id = item["product_id"]
            quantity = item["quantity"]

            stock = await repo.reserve(product_id, quantity)
            if stock is None:
                logger.warning(
                    "Reserve failed: order_id=%s, product_id=%s, quantity=%s",
                    order_id, product_id, quantity,
                )
                for r in reserved:
                    await repo.release(r["product_id"], r["quantity"])

                await _publish(
                    event_type="inventory.failed",
                    payload={
                        "order_id": order_id,
                        "product_id": product_id,
                        "quantity": quantity,
                        "reason": "insufficient_or_not_found",
                    },
                )
                return
            
            reserved.append({"product_id": product_id, "quantity": quantity})

        await _publish(
            event_type = "inventory.reserved",
            payload = {
                "order_id": order_id,
                "items": reserved
            }
        )
        logger.info("Reserved all items for order_id=%s", order_id)


async def _publish(event_type: str, payload: dict) -> None:
    """Публикует событие в inventory.events через outbox."""
    from app.outbox import enqueue_event
    from app.models import OutboxMessage

    async with SessionLocal() as session:
        await enqueue_event(session, event_type, payload)
        await session.commit()



        
