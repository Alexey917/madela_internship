import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random

from broker import connect_robust, declare_exchange, publish

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("catalog")

# ---------- models ----------
class Product(BaseModel):
    id: int
    name: str
    price: float
    stock: int
    category: str

class ReserveItem(BaseModel):
    product_id: int
    qty: int = 1

class ReserveIn(BaseModel):
    items: List[ReserveItem]

# --- generate 100 mock goods (deterministic) ---
_rng = random.Random(42)
_categories = ["books", "electronics", "toys", "food", "clothes", "sport", "home", "beauty"]
_adjectives = ["Pro", "Mini", "Eco", "Turbo", "Classic", "Smart", "Prime", "Ultra", "Neo", "Max"]
_nouns = ["Lamp", "Book", "Mouse", "Keyboard", "Ball", "Shirt", "Mug", "Phone", "Speaker", "Backpack",
          "Watch", "Shoes", "Game", "Tea", "Coffee", "Chair", "Desk", "Headphones", "Camera", "Bike"]

PRODUCTS: Dict[int, dict] = {}
for i in range(1, 101):
    name = f"{_rng.choice(_adjectives)} {_rng.choice(_nouns)} {i:03d}"
    price = round(_rng.uniform(5, 500), 2)
    # every 17th item out of stock to demo saga compensation
    stock = 0 if i % 17 == 0 else _rng.randint(1, 20)
    PRODUCTS[i] = {
        "id": i,
        "name": name,
        "price": price,
        "stock": stock,
        "category": _rng.choice(_categories),
    }
_initial_stock = {k: v["stock"] for k, v in PRODUCTS.items()}

# reservations: id -> {id, items, status}
RESERVATIONS: Dict[int, dict] = {}
_next_reservation_id = 1
_lock = asyncio.Lock()

# ---------- broker state ----------
_broker_conn = None
_broker_channel = None
_broker_exchange = None
broker_ready = False

# ---------- core domain logic (shared by HTTP + broker) ----------
def do_reserve(items: List[dict]) -> dict:
    """Validate + deduct stock. Raises HTTPException on error. Returns reservation dict."""
    global _next_reservation_id
    for it in items:
        pid, qty = it["product_id"], it.get("qty", 1)
        p = PRODUCTS.get(pid)
        if not p:
            raise HTTPException(404, f"product {pid} not found")
        if qty < 1:
            raise HTTPException(400, "qty must be >= 1")
        if p["stock"] < qty:
            raise HTTPException(409, f"insufficient stock for {p['name']}: have {p['stock']}, need {qty}")
    priced = []
    for it in items:
        p = PRODUCTS[it["product_id"]]
        p["stock"] -= it.get("qty", 1)
        priced.append({"product_id": p["id"], "name": p["name"], "price": p["price"], "qty": it.get("qty", 1)})
    rid = _next_reservation_id
    _next_reservation_id += 1
    RESERVATIONS[rid] = {"id": rid, "items": priced, "status": "reserved"}
    total = round(sum(i["price"] * i["qty"] for i in priced), 2)
    return {"reservation_id": rid, "items": priced, "total": total, "status": "reserved"}

def do_confirm(reservation_id: int) -> dict:
    r = RESERVATIONS.get(reservation_id)
    if not r:
        raise HTTPException(404, "reservation not found")
    if r["status"] != "reserved":
        raise HTTPException(409, f"reservation already {r['status']}")
    r["status"] = "confirmed"
    return r

def do_cancel(reservation_id: int) -> dict:
    r = RESERVATIONS.get(reservation_id)
    if not r:
        raise HTTPException(404, "reservation not found")
    if r["status"] == "cancelled":
        return r
    if r["status"] == "reserved":
        for it in r["items"]:
            PRODUCTS[it["product_id"]]["stock"] += it["qty"]
        r["status"] = "cancelled"
        return r
    raise HTTPException(409, f"cannot cancel {r['status']} reservation")

# ---------- broker consumer ----------
async def on_order_event(message) -> None:
    async with message.process():
        rk = message.routing_key or ""
        try:
            evt = json.loads(message.body.decode())
        except Exception:
            log.warning("bad message on %s: %r", rk, message.body[:200])
            return
        order_id = evt.get("order_id")
        log.info("recv %s for order %s", rk, order_id)
        try:
            async with _lock:
                if rk == "order.created":
                    try:
                        res = do_reserve(evt.get("items", []))
                        await publish(_broker_exchange, "stock.reserved", {
                            "order_id": order_id, **res,
                        })
                        log.info("order %s reserved -> %s", order_id, res["reservation_id"])
                    except HTTPException as e:
                        await publish(_broker_exchange, "stock.rejected", {
                            "order_id": order_id, "reason": str(e.detail),
                        })
                        log.info("order %s rejected: %s", order_id, e.detail)
                elif rk == "order.confirmed":
                    try:
                        r = do_confirm(evt["reservation_id"])
                        await publish(_broker_exchange, "stock.confirmed", {
                            "order_id": order_id, "reservation_id": r["id"],
                        })
                    except HTTPException as e:
                        await publish(_broker_exchange, "stock.confirm_failed", {
                            "order_id": order_id, "reservation_id": evt.get("reservation_id"),
                            "reason": str(e.detail),
                        })
                elif rk == "order.cancelled":
                    try:
                        r = do_cancel(evt["reservation_id"])
                        await publish(_broker_exchange, "stock.cancelled", {
                            "order_id": order_id, "reservation_id": r["id"],
                        })
                    except HTTPException as e:
                        await publish(_broker_exchange, "stock.cancel_failed", {
                            "order_id": order_id, "reservation_id": evt.get("reservation_id"),
                            "reason": str(e.detail),
                        })
                else:
                    log.warning("unknown routing key %s", rk)
        except Exception:
            log.exception("failed handling %s", rk)


async def broker_startup() -> None:
    global _broker_conn, _broker_channel, _broker_exchange, broker_ready
    try:
        _broker_conn = await connect_robust()
        _broker_channel = await _broker_conn.channel()
        await _broker_channel.set_qos(prefetch_count=10)
        _broker_exchange = await declare_exchange(_broker_channel)
        queue = await _broker_channel.declare_queue("catalog.order-events", durable=True)
        await queue.bind(_broker_exchange, routing_key="order.*")
        await queue.consume(on_order_event)
        broker_ready = True
        log.info("catalog subscribed: catalog.order-events <- order.*")
    except Exception:
        log.exception("catalog broker startup failed (HTTP fallback still works)")
        broker_ready = False

async def broker_shutdown() -> None:
    global broker_ready
    broker_ready = False
    try:
        if _broker_conn:
            await _broker_conn.close()
    except Exception:
        pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker_startup()
    yield
    await broker_shutdown()

app = FastAPI(title="Catalog Mock Service (event-driven)", lifespan=lifespan)

@app.get("/health")
def health():
    return {"service": "catalog", "status": "ok", "products": len(PRODUCTS),
            "broker": "up" if broker_ready else "down", "reservations": len(RESERVATIONS)}

@app.get("/products", response_model=List[Product])
def list_products():
    return list(PRODUCTS.values())

@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    p = PRODUCTS.get(product_id)
    if not p:
        raise HTTPException(404, "product not found")
    return p

@app.post("/reserve")
def reserve(payload: ReserveIn):
    """Saga step 1 (sync fallback): check stock + hold items."""
    return do_reserve([i.model_dump() for i in payload.items])

@app.post("/confirm/{reservation_id}")
def confirm(reservation_id: int):
    """Saga step 3 (sync fallback)."""
    return do_confirm(reservation_id)

@app.post("/cancel/{reservation_id}")
def cancel(reservation_id: int):
    """Saga compensation (sync fallback)."""
    return do_cancel(reservation_id)

@app.post("/reset")
def reset():
    """Restore initial stock (demo helper)."""
    for pid, stock in _initial_stock.items():
        PRODUCTS[pid]["stock"] = stock
    RESERVATIONS.clear()
    return {"status": "reset", "products": len(PRODUCTS)}
