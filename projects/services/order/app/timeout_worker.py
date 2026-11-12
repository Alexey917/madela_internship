import asyncio, logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.db import SessionLocal
from app.models import Order, OrderStatus, SagaState, SagaStatus
from app.saga import SagaService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 30
CHECK_INTERVAL = 5

async def timeout_worker() -> None:
    while True:
        try:
            async with SessionLocal() as session:
                cutoff = datetime.now(timezone.utc) - timedelta(seconds=TIMEOUT_SECONDS)

                # PENDING (inventory.reserve не ответил)
                pending = await session.execute(
                    select(SagaState).where(
                        SagaState.status == SagaStatus.PENDING,
                        SagaState.updated_at < cutoff,
                    )
                )
                for saga_state in pending.scalars().all():
                    saga = SagaService(session)
                    await saga.on_inventory_failed(saga_state.order_id, "timeout_inventory")

                # RESERVED (payment.process не ответил)
                reserved = await session.execute(
                    select(SagaState).where(
                        SagaState.status == SagaStatus.RESERVED,
                        SagaState.updated_at < cutoff,
                    )
                )
                for saga_state in reserved.scalars().all():
                    saga = SagaService(session)
                    await saga.on_payment_failed(saga_state.order_id, "timeout_payment")

        except Exception:
            logger.exception("Timeout worker error")
        await asyncio.sleep(CHECK_INTERVAL)