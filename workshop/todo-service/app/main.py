from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings


app = FastAPI(title=settings.service_name)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}