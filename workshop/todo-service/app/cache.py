import json, logging
from typing import Any

import redis.asyncio as aioredis

from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


redis_client: aioredis.Redis = aioredis.from_url(
  settings.redis_url,
  encoding="utf-8",
  decode_responses=True
)


async def get_json(key: str) -> Any | None:
    raw = await redis_client.get(key)
    if raw is None:
        return None
    return json.loads(raw)


async def set_json(key: str, value: Any, ttl: int=60) -> None:
    await redis_client.set(key, json.dumps(value, default=str), ex=ttl)


async def delete_pattern(pattern: str) -> int:
    """Удаляет все ключи, подходящие под паттерн. Возвращает количество."""
    count = 0
    async for key in redis_client.scan_iter(match=pattern):
        await redis_client.delete(key)
        count += 1
    return count