"""Shared RabbitMQ helper (topic exchange ``shop``).

Routing keys (demo saga):
  orders  -> catalog : ``order.created``   {order_id, customer, items}
                          ``order.confirmed`` {order_id, reservation_id}
                          ``order.cancelled`` {order_id, reservation_id, reason}
  catalog -> orders  : ``stock.reserved``  {order_id, reservation_id, items, total}
                          ``stock.rejected``  {order_id, reason}
                          ``stock.confirmed`` {order_id, reservation_id}
                          ``stock.cancelled`` {order_id, reservation_id}
"""
import asyncio
import json
import logging
import os

import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractChannel, AbstractExchange

log = logging.getLogger("broker")

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
EXCHANGE_NAME = os.getenv("EXCHANGE_NAME", "shop")


async def connect_robust(retries: int = 30, delay: float = 2.0) -> AbstractRobustConnection:
    last: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            conn = await aio_pika.connect_robust(RABBITMQ_URL)
            log.info("connected to rabbitmq (attempt %d)", attempt)
            return conn
        except Exception as e:  # noqa: BLE001 - retry on any conn error
            last = e
            log.warning("rabbitmq connect attempt %d/%d failed: %s", attempt, retries, e)
            await asyncio.sleep(delay)
    raise RuntimeError(f"cannot connect to rabbitmq {RABBITMQ_URL}: {last}")


async def declare_exchange(channel: AbstractChannel) -> AbstractExchange:
    exchange = await channel.declare_exchange(EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True)
    return exchange


async def publish(exchange: AbstractExchange, routing_key: str, payload: dict) -> None:
    body = json.dumps(payload, default=str).encode()
    await exchange.publish(
        aio_pika.Message(body=body, content_type="application/json", delivery_mode=2),
        routing_key=routing_key,
    )
