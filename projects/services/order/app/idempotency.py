from typing import Any
from fastapi import Request, HTTPException, status

from app.cache import get_json, set_json

IDEMPOTENCY_TTL = 60 * 60 * 24


async def check_idempotency(request: Request) -> str:
    """Возвращает Idempotency-Key или бросает 400, если его нет."""
    key = request.headers.get("Idempotency-Key")

    if not key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idempotency-Key header is required",
        )

    return key


async def get_cached_response(key: str) -> dict[str, Any]:
    """Возвращает закешированный ответ или None."""
    return await get_json(f"idem:{key}")


async def store_response(key: str, status_code: int, body: dict[str, Any]) -> None:
    """Сохраняет ответ в Redis с TTL 24ч."""
    await set_json(
        f"idem:{key}",
        {"status_code": status_code, "body": body},
        ttl=IDEMPOTENCY_TTL,
    )