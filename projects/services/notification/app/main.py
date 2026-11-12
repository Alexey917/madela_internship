import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.broker import broker
from app.consumer import start_order_events_consumer, start_payment_events_consumer
from app.db import engine



@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.connect()
    order_consumer_task = asyncio.create_task(start_order_events_consumer())
    payment_consumer_task = asyncio.create_task(start_payment_events_consumer())

    yield

    for task in (order_consumer_task, payment_consumer_task):
        task.cancel()
    for task in (order_consumer_task, payment_consumer_task):
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