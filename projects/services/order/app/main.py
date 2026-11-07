import asyncio
from contextlib  import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI

from app.config import settings
from app.db import engine
from app.broker import broker
from app.outbox import outbox_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.connection()
    worker_task = asyncio.create_task(outbox_worker())

    yield

    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass

    await broker.close()
    await engine.dispose()


app = FastAPI(title=settings.service_name, lifespan=lifespan)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}