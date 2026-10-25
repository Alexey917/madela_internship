import json
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse

from app.dependencies import get_repo
from app.repository import StockRepository
from app.schemas import (
  StockRead, 
  StockCommitRequest, 
  StockReserveRequest, 
  StockReleaseRequest
)
from app.idempotency import (
    get_cached_response,
    check_idempotency,
    store_response
)

router = APIRouter(prefix="/stock", tags=["stock"])


@router.get("/{product_id}", response_model = StockRead)
async def get_stock(
    product_id: int, 
    repo: StockRepository = Depends(get_repo)
) -> StockRead:
    stock = await repo.get(product_id)

    if stock is None:
        raise HTTPException(status_code = 404, detail = "Stock not found")

    return StockRead.model_validate(stock)


@router.post("/reserve", response_model = StockRead)
async def reserve_stock(
    data: StockReserveRequest,
    request: Request,
    repo: StockRepository = Depends(get_repo)
) -> StockRead:
    idempotency_key = await check_idempotency(request)

    cached = await get_cached_response(idempotency_key)

    if cached is not None:
        return JSONResponse(
            status_code = cached["status_code"],
            content = cached["body"]
        )

    stock = await repo.reserve(data.product_id, data.quantity)

    if stock is None:
        existing = await repo.get(data.product_id)

        if existing is None:
            response = JSONResponse(
                status_code = 404, detail = "Stock not found"
            )
        else:
            response = JSONResponse(
                status_code=409,
                content={"detail": "Insufficient stock"},
            )

        await store_response(idempotency_key, response.status_code, json.loads(response.body))
        return response

    result = StockRead.model_validate(stock)
    response_body = result.model_dump(mode="json")
    await store_response(idempotency_key, 200, response_body)
    return result


@router.post("/commit", response_model = StockRead)
async def commit_stock(
    data: StockCommitRequest,
    request: Request,
    repo: StockRepository = Depends(get_repo)    
) -> StockRead:
    idempotency_key = await check_idempotency(request)
    
    cached = await get_cached_response(idempotency_key)

    if cached is not None:
        return JSONResponse(
            status_code = cached["status_code"],
            content = cached["body"]
        )
    
    stock = await repo.commit(data.product_id, data.quantity)

    if stock is None:
        body = {"detail": "Cannot commit: insufficient reserved"}
        await store_response(idempotency_key, 409, body)
        return JSONResponse(status_code=409, content=body)

    result = StockRead.model_validate(stock)
    body = result.model_dump(mode="json")
    await store_response(idempotency_key, 200, body)
    return result


@router.post("/release", response_model = StockRead)
async def commit_stock(
    data: StockReserveRequest,
    request: Request,
    repo: StockRepository = Depends(get_repo)    
) -> StockRead:
    idempotency_key = await check_idempotency(request)
        
    cached = await get_cached_response(idempotency_key)
    
    if cached is not None:
        return JSONResponse(
            status_code = cached["status_code"],
            content = cached["body"]
        )
    
    stock = await repo.release(data.product_id, data.quantity)

    if stock is None:
        body = {"detail": "Cannot release: insufficient reserved"}
        await store_response(idempotency_key, 409, body)
        return JSONResponse(status_code=409, content=body)

    result = StockRead.model_validate(stock)
    body = result.model_dump(mode="json")
    await store_response(idempotency_key, 200, body)
    return result