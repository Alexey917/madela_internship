import aio_pika, json
from aio_pika import ExchangeType, Message
from typing import Any

from app.config import settings

class Broker:
    def __init__(self) -> None:
        self._connection: aio_pika.RobustConnection | None = None
        self._channel: aio_pika.RobustChannel  | None = None


    async def connection(self) -> None:
        self._connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        self._channel = await self._connection.channel()


    async def close(self) -> None:
        if self._connection:
            await self._connection.close()


broker = Broker()