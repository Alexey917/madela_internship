from contextlib import asynccontextmanager
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.db import engine
from app.routers import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title=settings.service_name, lifespan=lifespan)
app.include_router(auth.router)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_name}