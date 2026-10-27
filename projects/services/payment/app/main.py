from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.cache import redis_client
from app.config import settings
from app.db import engine
from app.mock_gateway import router as mock_gateway_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()
    await redis_client.aclose()


app = FastAPI(title=settings.service_name, lifespan=lifespan)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.include_router(mock_gateway_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}