import json
from typing import Any

import redis.asyncio as aioredis

from app.config import settings


redis_client: aioredis.Redis = aioredis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
)


async def get_json(key: str) -> Any | None:
    raw = await redis_client.get(key)
    if raw is None:
        return None
    return json.loads(raw)


async def set_json(key: str, value: Any, ttl: int = 60) -> None:
    await redis_client.set(key, json.dumps(value, default=str), ex=ttl)
