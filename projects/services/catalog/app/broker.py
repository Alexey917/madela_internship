import json
from typing import Any

import aio_pika
from aio_pika import ExchangeType, Message

from app.config import settings

EXCHANGE_NAME = "catalog.events"


class Broker:
    def __init__(self) -> None:
        self._connection: aio_pika.RobustConnection | None = None
        self._channel: aio_pika.RobustChannel | None = None
        self._exchange: aio_pika.RobustExchange | None = None


    async def connection(self) -> None:
        self._connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        self._channel = await self._connection.channel()
        self._exchange = await self._channel.declare_exchange(EXCHANGE_NAME, ExchangeType.TOPIC, durable=True)


    async def close(self) -> None:
        if self._connection:
            await self._connection.close()


    async def publish(self, routing_key: str, payload: dict[str, Any]) -> None:
        if self._exchange is None:
            raise RuntimeError("Broker is connected")

        message = Message(
            body = json.dumps(payload, default = str).encode(),
            content_type = "application/json",
            delivery_mode = aio_pika.DeliveryMode.PERSISTENT,
        )

        await self._exchange.publish(message, routing_key)


broker = Broker()