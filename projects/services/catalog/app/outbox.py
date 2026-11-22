import json, asyncio, logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.models import OutboxMessage
from app.broker import broker
from app.db import SessionLocal


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BATCH_SIZE = 100
POOL_INTERVAL = 1.0


async def enqueue_event(
    session: AsyncSession,
    event_type: str,
    payload: dict[str, Any]
) -> None:
    """Добавляет событие в outbox. Коммит — на вызывающей стороне."""
    message = OutboxMessage(
        event_type = event_type,
        routing_key = event_type,
        payload = json.loads(json.dumps(payload, default = str))
    )

    session.add(message)
    print(f"OUTBOX_ADDED: {event_type}, session={id(session)}, message_id={id(message)}", flush=True)


async def outbox_worker() -> None:
    """Бесконечный цикл: публикует неопубликованные outbox-сообщения."""
    logger.info("Outbox worker started")
    while True:
        try:
            async with SessionLocal() as session:
                await _process_batch(session)
        except asyncio.CancelledError:
            logger.info("Outbox worker stopped")
            raise
        except Exception:
            logger.exception("Outbox worker error")
        await asyncio.sleep(POOL_INTERVAL)


async def _process_batch(session: AsyncSession) -> None:
    result = await session.execute(
        select(OutboxMessage)
        .where(OutboxMessage.published_at.is_(None))
        .order_by(OutboxMessage.id)
        .limit(BATCH_SIZE)
        .with_for_update(skip_locked=True)
    )
    messages = result.scalars().all()

    if messages is None:
        return None

    for msg in messages:
        await broker.publish(msg.routing_key, msg.payload)
        msg.published_at = datetime.now(timezone.utc)

    await session.commit()
    logger.info("Published %d outbox messages", len(messages))
