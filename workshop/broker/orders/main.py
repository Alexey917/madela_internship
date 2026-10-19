import asyncio
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

from broker import connect_robust, declare_exchange, publish

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("orders")

CATALOG_URL = os.getenv("CATALOG_URL", "http://localhost:8002")
TIMEOUT = 10.0
SAGA_STEP_TIMEOUT = float(os.getenv("SAGA_STEP_TIMEOUT", "10"))

# ---------- models ----------
class OrderIn(BaseModel):  # legacy simple order (kept for compat)
    customer: str
    item: str
    qty: int = 1

class CartItem(BaseModel):
    product_id: int
    qty: int = 1

class CheckoutIn(BaseModel):
    customer: str
    items: List[CartItem]

# ---------- storage ----------
# unified order shape: {id, customer, items, total, status, reservation_id, saga, transport, created_at}
ORDERS: List[dict] = [
    {"id": 1, "customer": "alice", "items": [{"product_id": 0, "name": "laptop", "price": 999.0, "qty": 1}],
     "total": 999.0, "status": "confirmed", "reservation_id": None, "saga": ["legacy seed"],
     "transport": "none", "created_at": time.time()},
    {"id": 2, "customer": "bob", "items": [{"product_id": 0, "name": "mouse", "price": 25.0, "qty": 2}],
     "total": 50.0, "status": "confirmed", "reservation_id": None, "saga": ["legacy seed"],
     "transport": "none", "created_at": time.time()},
]
_next_id = 3

# ---------- broker state ----------
_broker_conn = None
_broker_channel = None
_broker_exchange = None
broker_ready = False
# pending futures: key "order_id:stage" -> Future[dict]; stages: "stock", "final"
_pending: Dict[str, asyncio.Future] = {}

def _key(order_id: int, stage: str) -> str:
    return f"{order_id}:{stage}"

async def _wait_for(order_id: int, stage: str, timeout: float) -> dict:
    loop = asyncio.get_running_loop()
    fut: asyncio.Future = loop.create_future()
    _pending[_key(order_id, stage)] = fut
    try:
        return await asyncio.wait_for(fut, timeout)
    finally:
        _pending.pop(_key(order_id, stage), None)

def _resolve(order_id: int, stage: str, payload: dict) -> None:
    fut = _pending.get(_key(order_id, stage))
    if fut and not fut.done():
        fut.set_result(payload)
    else:
        log.warning("no waiter for order %s stage %s (payload dropped)", order_id, stage)

async def on_stock_event(message) -> None:
    async with message.process():
        rk = message.routing_key or ""
        try:
            evt = json.loads(message.body.decode())
        except Exception:
            log.warning("bad stock message on %s", rk)
            return
        order_id = evt.get("order_id")
        log.info("recv %s for order %s", rk, order_id)
        if rk in ("stock.reserved", "stock.rejected"):
            _resolve(order_id, "stock", {"routing_key": rk, **evt})
        elif rk in ("stock.confirmed", "stock.confirm_failed", "stock.cancelled", "stock.cancel_failed"):
            _resolve(order_id, "final", {"routing_key": rk, **evt})
        else:
            log.warning("unknown stock routing key %s", rk)

async def broker_startup() -> None:
    global _broker_conn, _broker_channel, _broker_exchange, broker_ready
    try:
        _broker_conn = await connect_robust()
        _broker_channel = await _broker_conn.channel()
        await _broker_channel.set_qos(prefetch_count=20)
        _broker_exchange = await declare_exchange(_broker_channel)
        queue = await _broker_channel.declare_queue("orders.stock-events", durable=True)
        await queue.bind(_broker_exchange, routing_key="stock.*")
        await queue.consume(on_stock_event)
        broker_ready = True
        log.info("orders subscribed: orders.stock-events <- stock.*")
    except Exception:
        log.exception("orders broker startup failed (will use HTTP fallback)")
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

app = FastAPI(title="Orders Service + Saga Orchestrator (event-driven)", lifespan=lifespan)

# ---------- helpers ----------
def mock_payment(total: float, customer: str) -> dict:
    """Simple mock payment: fails to demo saga compensation.
    Rules: customer == 'fail' -> decline; total > 3000 -> limit exceeded."""
    if customer.strip().lower() == "fail":
        return {"ok": False, "reason": "card declined (mock: customer=fail)"}
    if total > 3000:
        return {"ok": False, "reason": f"payment limit exceeded: total {total} > 3000 (mock)"}
    return {"ok": True, "transaction_id": f"pay-{int(time.time()*1000)}"}

@app.get("/health")
def health():
    return {"service": "orders", "status": "ok",
            "broker": "up" if broker_ready else "down", "orders": len(ORDERS)}

@app.get("/orders")
def list_orders():
    return ORDERS

@app.get("/orders/{order_id}")
def get_order(order_id: int):
    for o in ORDERS:
        if o["id"] == order_id:
            return o
    raise HTTPException(404, "order not found")

@app.post("/orders", status_code=201)
def create_order_legacy(payload: OrderIn):
    """Legacy simple order (no saga)."""
    global _next_id
    order = {
        "id": _next_id, "customer": payload.customer,
        "items": [{"product_id": 0, "name": payload.item, "price": 0.0, "qty": payload.qty}],
        "total": 0.0, "status": "pending", "reservation_id": None,
        "saga": ["legacy create (no saga)"], "transport": "none", "created_at": time.time(),
    }
    ORDERS.append(order)
    _next_id += 1
    return order

# ---------- saga via HTTP (fallback, original behavior) ----------
async def _checkout_http(order: dict, saga: List[str], payload: CheckoutIn):
    order["transport"] = "http-fallback"
    saga.append(f"1. order {order['id']} created PENDING for {payload.customer} (transport=http)")
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as c:
            r = await c.post(f"{CATALOG_URL}/reserve",
                             json={"items": [i.model_dump() for i in payload.items]})
    except Exception as e:
        raise HTTPException(502, f"catalog unreachable: {e}")

    if r.status_code != 200:
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        order["status"] = "failed"
        saga.append(f"2. RESERVE failed -> abort: {detail}")
        raise HTTPException(status_code=409, detail={"error": "reserve failed", "catalog_detail": detail, "order": order})

    res = r.json()
    order["reservation_id"] = res["reservation_id"]
    order["items"] = res["items"]
    order["total"] = res["total"]
    saga.append(f"2. RESERVE ok: reservation {res['reservation_id']}, total={res['total']}")

    pay = mock_payment(order["total"], payload.customer)
    if not pay["ok"]:
        saga.append(f"3. PAYMENT failed: {pay['reason']}")
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as c:
                cr = await c.post(f"{CATALOG_URL}/cancel/{order['reservation_id']}")
            saga.append(f"4. COMPENSATION ok: reservation {order['reservation_id']} cancelled, stock restored"
                        if cr.status_code == 200 else
                        f"4. COMPENSATION FAILED: catalog cancel -> {cr.text}")
        except Exception as e:
            saga.append(f"4. COMPENSATION FAILED: {e}")
        order["status"] = "cancelled"
        raise HTTPException(status_code=402, detail={"error": "payment failed, compensated", "reason": pay["reason"], "order": order})

    saga.append(f"3. PAYMENT ok: {pay['transaction_id']} total={order['total']}")
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as c:
            cr = await c.post(f"{CATALOG_URL}/confirm/{order['reservation_id']}")
    except Exception as e:
        order["status"] = "failed"
        saga.append(f"4. CONFIRM error: {e}")
        raise HTTPException(502, f"catalog confirm unreachable: {e}")
    if cr.status_code != 200:
        order["status"] = "failed"
        saga.append(f"4. CONFIRM failed: {cr.text} (manual intervention needed)")
        raise HTTPException(500, f"confirm failed: {cr.text}")
    order["status"] = "confirmed"
    saga.append(f"4. CONFIRM ok: reservation {order['reservation_id']} confirmed -> order CONFIRMED")
    return order

# ---------- saga via broker (primary) ----------
async def _checkout_broker(order: dict, saga: List[str], payload: CheckoutIn):
    order_id = order["id"]
    order["transport"] = "broker"
    saga.append(f"1. order {order_id} created PENDING for {payload.customer} (transport=broker: publish order.created)")

    await publish(_broker_exchange, "order.created", {
        "order_id": order_id, "customer": payload.customer,
        "items": [i.model_dump() for i in payload.items],
    })
    try:
        stock = await _wait_for(order_id, "stock", SAGA_STEP_TIMEOUT)
    except asyncio.TimeoutError:
        order["status"] = "failed"
        saga.append(f"2. RESERVE timeout: no stock.* event in {SAGA_STEP_TIMEOUT}s (catalog down?)")
        raise HTTPException(504, f"reserve timeout: catalog did not respond via broker")

    if stock["routing_key"] == "stock.rejected":
        order["status"] = "failed"
        saga.append(f"2. RESERVE failed via broker -> abort: {stock.get('reason')}")
        raise HTTPException(status_code=409, detail={"error": "reserve failed", "catalog_detail": stock.get("reason"), "order": order})

    order["reservation_id"] = stock["reservation_id"]
    order["items"] = stock["items"]
    order["total"] = stock["total"]
    saga.append(f"2. RESERVE ok via broker: reservation {stock['reservation_id']}, total={stock['total']} (stock.reserved)")

    pay = mock_payment(order["total"], payload.customer)
    if not pay["ok"]:
        saga.append(f"3. PAYMENT failed: {pay['reason']} -> publish order.cancelled (compensation)")
        await publish(_broker_exchange, "order.cancelled", {
            "order_id": order_id, "reservation_id": order["reservation_id"], "reason": pay["reason"],
        })
        try:
            fin = await _wait_for(order_id, "final", SAGA_STEP_TIMEOUT)
            if fin["routing_key"] == "stock.cancelled":
                saga.append(f"4. COMPENSATION ok via broker: reservation {order['reservation_id']} cancelled, stock restored (stock.cancelled)")
            else:
                saga.append(f"4. COMPENSATION FAILED via broker: {fin}")
        except asyncio.TimeoutError:
            saga.append(f"4. COMPENSATION sent, no stock.cancelled ack in {SAGA_STEP_TIMEOUT}s (assumed cancelled)")
        order["status"] = "cancelled"
        raise HTTPException(status_code=402, detail={"error": "payment failed, compensated", "reason": pay["reason"], "order": order})

    saga.append(f"3. PAYMENT ok: {pay['transaction_id']} total={order['total']} -> publish order.confirmed")
    await publish(_broker_exchange, "order.confirmed", {
        "order_id": order_id, "reservation_id": order["reservation_id"],
    })
    try:
        fin = await _wait_for(order_id, "final", SAGA_STEP_TIMEOUT)
    except asyncio.TimeoutError:
        order["status"] = "failed"
        saga.append(f"4. CONFIRM timeout: no stock.confirmed in {SAGA_STEP_TIMEOUT}s (manual intervention needed)")
        raise HTTPException(504, "confirm timeout: catalog did not respond via broker")
    if fin["routing_key"] != "stock.confirmed":
        order["status"] = "failed"
        saga.append(f"4. CONFIRM failed via broker: {fin} (manual intervention needed)")
        raise HTTPException(500, f"confirm failed via broker: {fin}")
    order["status"] = "confirmed"
    saga.append(f"4. CONFIRM ok via broker: reservation {order['reservation_id']} confirmed -> order CONFIRMED (stock.confirmed)")
    return order

@app.post("/orders/checkout", status_code=201)
async def checkout(payload: CheckoutIn):
    """Saga orchestrator over RabbitMQ (falls back to sync HTTP if broker down).

    Event flow (topic exchange ``shop``):
      orders --order.created--> catalog --stock.reserved/rejected--> orders
        (payment inside orders)
      orders --order.confirmed/cancelled--> catalog --stock.confirmed/cancelled--> orders
    """
    global _next_id
    if not payload.items:
        raise HTTPException(400, "bucket is empty")

    order_id = _next_id
    _next_id += 1
    saga: List[str] = []
    order = {
        "id": order_id, "customer": payload.customer,
        "items": [], "total": 0.0, "status": "pending",
        "reservation_id": None, "saga": saga, "transport": "broker",
        "created_at": time.time(),
    }
    ORDERS.append(order)

    if broker_ready and _broker_exchange is not None:
        try:
            return await _checkout_broker(order, saga, payload)
        except HTTPException:
            raise
        except Exception as e:  # noqa: BLE001
            log.exception("broker saga crashed, no HTTP retry (order %s)", order_id)
            order["status"] = "failed"
            saga.append(f"broker error: {e}")
            raise HTTPException(500, f"broker saga failed: {e}")
    else:
        log.warning("broker down, using HTTP fallback for order %s", order_id)
        return await _checkout_http(order, saga, payload)
