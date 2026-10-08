# Simple FastAPI API Gateway + Catalog + Saga Orders

Demo: gateway proxies to catalog (100 mock goods) and orders (saga orchestrator). HTML shop: catalog → bucket → buy.

```
gateway/  :8000  -> serves HTML + proxies /api/products*, /api/orders*, /api/checkout
catalog/  :8002  -> 100 mock products, POST /reserve, /confirm/{id}, /cancel/{id}
orders/   :8001  -> saga orchestrator POST /orders/checkout
```

## Run

```bash
docker compose up --build
```

Open:
- Shop: http://localhost:8000
- Gateway health: http://localhost:8000/health
- Catalog: http://localhost:8000/api/products
- Orders: http://localhost:8000/api/orders
- Docs: http://localhost:8000/docs, http://localhost:8001/docs, http://localhost:8002/docs

Local (no docker):

```bash
# t1 catalog
uvicorn main:app --port 8002 --app-dir catalog
# t2 orders
CATALOG_URL=http://localhost:8002 uvicorn main:app --port 8001 --app-dir orders
# t3 gateway
ORDERS_URL=http://localhost:8001 CATALOG_URL=http://localhost:8002 uvicorn main:app --port 8000 --app-dir gateway
```

## Saga (orchestration, in orders service)

`POST /api/checkout {"customer","items":[{"product_id","qty"}]}`:

1. create order `PENDING` + saga log `[]`
2. `POST catalog/reserve` — fail (e.g. stock 0, every 17th product) → order `FAILED`, abort, no compensation needed
3. mock payment — fail if `customer=="fail"` or `total>3000` → **compensate** `POST catalog/cancel/{reservation_id}` (restore stock), order `CANCELLED`
4. `POST catalog/confirm/{reservation_id}` → order `CONFIRMED`

Each order stores `saga: [...]` trace, visible in UI and `GET /api/orders/{id}`.

Test:

```bash
curl localhost:8000/api/products | head -c 300
# success
curl -X POST localhost:8000/api/checkout -H 'Content-Type: application/json' \
  -d '{"customer":"dave","items":[{"product_id":1,"qty":1},{"product_id":2,"qty":2}]}'
# out-of-stock -> 409 (product 17 has stock 0)
curl -X POST localhost:8000/api/checkout -H 'Content-Type: application/json' \
  -d '{"customer":"dave","items":[{"product_id":17,"qty":1}]}'
# payment fail -> 402 + compensation (customer=fail)
curl -X POST localhost:8000/api/checkout -H 'Content-Type: application/json' \
  -d '{"customer":"fail","items":[{"product_id":1,"qty":1}]}'
# reset catalog stock
curl -X POST localhost:8000/api/catalog/reset
```

## API table

| Gateway | Proxied to |
|---------|------------|
| `GET /api/products` | `GET catalog/products` |
| `GET /api/products/{id}` | `GET catalog/products/{id}` |
| `GET /api/orders` | `GET orders/orders` |
| `POST /api/checkout` | `POST orders/orders/checkout` (saga) |
| `POST /api/orders` | `POST orders/orders` (legacy) |
