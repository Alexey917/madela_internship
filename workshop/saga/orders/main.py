import os
import time
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI(title="Orders Service + Saga Orchestrator")

CATALOG_URL = os.getenv("CATALOG_URL", "http://localhost:8002")
TIMEOUT = 10.0

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
# unified order shape: {id, customer, items:[{product_id,name,price,qty}], total, status, reservation_id, saga:[], created_at}
ORDERS: List[dict] = [
    {"id": 1, "customer": "alice", "items": [{"product_id": 0, "name": "laptop", "price": 999.0, "qty": 1}],
     "total": 999.0, "status": "confirmed", "reservation_id": None, "saga": ["legacy seed"], "created_at": time.time()},
    {"id": 2, "customer": "bob", "items": [{"product_id": 0, "name": "mouse", "price": 25.0, "qty": 2}],
     "total": 50.0, "status": "confirmed", "reservation_id": None, "saga": ["legacy seed"], "created_at": time.time()},
]
_next_id = 3

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
    return {"service": "orders", "status": "ok"}

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
        "saga": ["legacy create (no saga)"], "created_at": time.time(),
    }
    ORDERS.append(order)
    _next_id += 1
    return order

@app.post("/orders/checkout", status_code=201)
async def checkout(payload: CheckoutIn):
    """Saga orchestrator (orchestration style):
    1. create order PENDING
    2. RESERVE stock in catalog (POST /reserve)
    3. mock PAYMENT
       - on fail -> COMPENSATE: POST /cancel/{reservation_id}, mark order CANCELLED
    4. CONFIRM reservation (POST /confirm/{id}), mark order CONFIRMED
    Returns order with full `saga` trace.
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
        "reservation_id": None, "saga": saga, "created_at": time.time(),
    }
    ORDERS.append(order)

    def fail(status: str, msg: str):
        saga.append(msg)
        order["status"] = status
        return order

    # Step 1: order created
    saga.append(f"1. order {order_id} created PENDING for {payload.customer}")

    # Step 2: reserve in catalog
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
    reservation_id = res["reservation_id"]
    order["reservation_id"] = reservation_id
    order["items"] = res["items"]
    order["total"] = res["total"]
    saga.append(f"2. RESERVE ok: reservation {reservation_id}, total={res['total']}")

    # Step 3: mock payment
    pay = mock_payment(order["total"], payload.customer)
    if not pay["ok"]:
        saga.append(f"3. PAYMENT failed: {pay['reason']}")
        # compensation: cancel reservation
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as c:
                cr = await c.post(f"{CATALOG_URL}/cancel/{reservation_id}")
            if cr.status_code == 200:
                saga.append(f"4. COMPENSATION ok: reservation {reservation_id} cancelled, stock restored")
            else:
                saga.append(f"4. COMPENSATION FAILED: catalog cancel -> {cr.text}")
        except Exception as e:
            saga.append(f"4. COMPENSATION FAILED: {e}")
        order["status"] = "cancelled"
        raise HTTPException(status_code=402, detail={"error": "payment failed, compensated", "reason": pay["reason"], "order": order})

    saga.append(f"3. PAYMENT ok: {pay['transaction_id']} total={order['total']}")

    # Step 4: confirm reservation
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as c:
            cr = await c.post(f"{CATALOG_URL}/confirm/{reservation_id}")
    except Exception as e:
        order["status"] = "failed"
        saga.append(f"4. CONFIRM error: {e}")
        raise HTTPException(502, f"catalog confirm unreachable: {e}")

    if cr.status_code != 200:
        order["status"] = "failed"
        saga.append(f"4. CONFIRM failed: {cr.text} (manual intervention needed)")
        raise HTTPException(500, f"confirm failed: {cr.text}")

    order["status"] = "confirmed"
    saga.append(f"4. CONFIRM ok: reservation {reservation_id} confirmed -> order CONFIRMED")
    return order
