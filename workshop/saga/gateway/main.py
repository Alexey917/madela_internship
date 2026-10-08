import os
from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
import httpx

app = FastAPI(title="Simple API Gateway")

ORDERS_URL = os.getenv("ORDERS_URL", "http://localhost:8001")
CATALOG_URL = os.getenv("CATALOG_URL", "http://localhost:8002")
TIMEOUT = 10.0

async def check(url: str):
    try:
        async with httpx.AsyncClient(timeout=5.0) as c:
            r = await c.get(f"{url}/health")
            return r.json() if r.status_code == 200 else {"status": "unreachable"}
    except Exception as e:
        return {"status": "down", "error": str(e)}

@app.get("/health")
async def health():
    return {
        "gateway": "ok",
        "orders_service": await check(ORDERS_URL),
        "catalog_service": await check(CATALOG_URL),
    }

@app.get("/")
def index():
    return FileResponse("static/index.html")

async def proxy(base: str, method: str, path: str, body=None):
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.request(method, f"{base}{path}", json=body)
        return Response(
            content=r.content,
            status_code=r.status_code,
            media_type=r.headers.get("content-type", "application/json"),
        )

# --- orders (incl. saga checkout) ---
@app.get("/api/orders")
async def list_orders():
    return await proxy(ORDERS_URL, "GET", "/orders")

@app.get("/api/orders/{order_id}")
async def get_order(order_id: int):
    return await proxy(ORDERS_URL, "GET", f"/orders/{order_id}")

@app.post("/api/orders")
async def create_order(req: Request):
    return await proxy(ORDERS_URL, "POST", "/orders", await req.json())

@app.post("/api/checkout")
async def checkout(req: Request):
    """Bucket buy -> saga orchestrator in orders: POST /orders/checkout"""
    return await proxy(ORDERS_URL, "POST", "/orders/checkout", await req.json())

# --- catalog ---
@app.get("/api/products")
async def list_products():
    return await proxy(CATALOG_URL, "GET", "/products")

@app.get("/api/products/{product_id}")
async def get_product(product_id: int):
    return await proxy(CATALOG_URL, "GET", f"/products/{product_id}")

@app.post("/api/catalog/reset")
async def catalog_reset():
    return await proxy(CATALOG_URL, "POST", "/reset", None)
