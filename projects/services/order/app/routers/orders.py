from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.dependencies import get_repo, get_saga
from app.idempotency import (
    check_idempotency,
    get_cached_response,
    store_response,
)
from app.repository import OrderRepository
from app.saga import SagaService
from app.schemas import OrderCreate, OrderRead


router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: int,
    repo: OrderRepository = Depends(get_repo),
) -> OrderRead:
    order = await repo.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderRead.model_validate(order)


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
    data: OrderCreate,
    request: Request,
    repo: OrderRepository = Depends(get_repo),
    saga: SagaService = Depends(get_saga),
) -> OrderRead:
    idem_key = await check_idempotency(request)
    cached = await get_cached_response(idem_key)
    if cached is not None:
        return JSONResponse(status_code=cached["status_code"], content=cached["body"])

    order = await repo.create(
        user_id=data.user_id,
        items=[
            {
                "product_id": i.product_id,
                "quantity": i.quantity,
                "unit_price": i.unit_price,
            }
            for i in data.items
        ],
    )

    # Запускаем SAGA
    await saga.start(order.id)

    result = OrderRead.model_validate(order)
    body = result.model_dump(mode="json")
    await store_response(idem_key, 201, body)
    return result


@router.post("/{order_id}/cancel", response_model=OrderRead)
async def cancel_order(
    order_id: int,
    repo: OrderRepository = Depends(get_repo),
    saga: SagaService = Depends(get_saga),
) -> OrderRead:
    try:
        await saga.cancel(order_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    order = await repo.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderRead.model_validate(order)