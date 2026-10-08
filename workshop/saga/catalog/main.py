from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import random

app = FastAPI(title="Catalog Mock Service")

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

@app.get("/health")
def health():
    return {"service": "catalog", "status": "ok", "products": len(PRODUCTS)}

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
    """Saga step 1: check stock + hold items. Returns reservation_id + priced items."""
    global _next_reservation_id
    # validate first (no partial deduction)
    for it in payload.items:
        p = PRODUCTS.get(it.product_id)
        if not p:
            raise HTTPException(404, f"product {it.product_id} not found")
        if it.qty < 1:
            raise HTTPException(400, "qty must be >= 1")
        if p["stock"] < it.qty:
            raise HTTPException(409, f"insufficient stock for {p['name']}: have {p['stock']}, need {it.qty}")
    # deduct
    priced = []
    for it in payload.items:
        p = PRODUCTS[it.product_id]
        p["stock"] -= it.qty
        priced.append({"product_id": p["id"], "name": p["name"], "price": p["price"], "qty": it.qty})
    rid = _next_reservation_id
    _next_reservation_id += 1
    RESERVATIONS[rid] = {"id": rid, "items": priced, "status": "reserved"}
    total = round(sum(i["price"] * i["qty"] for i in priced), 2)
    return {"reservation_id": rid, "items": priced, "total": total, "status": "reserved"}

@app.post("/confirm/{reservation_id}")
def confirm(reservation_id: int):
    """Saga step 3 (success path): finalize reservation, stock stays deducted."""
    r = RESERVATIONS.get(reservation_id)
    if not r:
        raise HTTPException(404, "reservation not found")
    if r["status"] != "reserved":
        raise HTTPException(409, f"reservation already {r['status']}")
    r["status"] = "confirmed"
    return r

@app.post("/cancel/{reservation_id}")
def cancel(reservation_id: int):
    """Saga compensation: restore stock."""
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

@app.post("/reset")
def reset():
    """Restore initial stock (demo helper)."""
    for pid, stock in _initial_stock.items():
        PRODUCTS[pid]["stock"] = stock
    RESERVATIONS.clear()
    return {"status": "reset", "products": len(PRODUCTS)}
