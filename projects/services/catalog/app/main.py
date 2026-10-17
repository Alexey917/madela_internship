from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator 

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title = settings.service_name, lifespan = lifespan)
Instrumentator().instrument(app).expose(app, endpoint = "/metrics")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}