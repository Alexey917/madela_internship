import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.broker import broker
from app.cache import redis_client
from app.config import settings
from app.db import engine
from app.mock_gateway import router as mock_gateway_router
from app.outbox import outbox_worker
from app.routers import payment
from app.consumer import start_consumer


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.connect()
    worker_task = asyncio.create_task(outbox_worker())
    consumer_task = asyncio.create_task(start_consumer())

    yield

    consumer_task.cancel()
    worker_task.cancel()
    for task in (consumer_task, worker_task):
        try:
            await task
        except asyncio.CancelledError:
            pass


    await broker.close()
    await engine.dispose()
    await redis_client.aclose()


app = FastAPI(title=settings.service_name, lifespan=lifespan)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.include_router(mock_gateway_router)
app.include_router(payment.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}