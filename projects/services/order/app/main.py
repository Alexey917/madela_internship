import asyncio
from contextlib  import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI

from app.config import settings
from app.db import engine
from app.broker import broker
from app.outbox import outbox_worker
from app.consumer import start_inventory_consumer, start_payment_consumer
from app.timeout_worker import timeout_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.connection()
    worker_task = asyncio.create_task(outbox_worker())
    inv_consumer_task = asyncio.create_task(start_inventory_consumer())
    pay_consumer_task = asyncio.create_task(start_payment_consumer())
    timeout_task = asyncio.create_task(timeout_worker())

    yield

    for task in (inv_consumer_task, pay_consumer_task, worker_task, timeout_task):
        task.cancel()
    for task in (inv_consumer_task, pay_consumer_task, worker_task, timeout_task):
        try:
            await task
        except asyncio.CancelledError:
            pass

    await broker.close()
    await engine.dispose()


app = FastAPI(title=settings.service_name, lifespan=lifespan)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}