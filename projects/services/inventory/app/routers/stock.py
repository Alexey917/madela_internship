from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_repo
from app.repository import StockRepository
from app.schemas import (
  StockRead, 
  StockCommitRequest, 
  StockReserveRequest, 
  StockReleaseRequest
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
    repo: StockRepository = Depends(get_repo)
) -> StockRead:
    stock = await repo.reserve(data.product_id, data.quantity)

    if stock is None:
        existing = await repo.get(data.product_id)

        if existing is None:
            raise HTTPException(status_code = 404, detail = "Stock not found")

        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = "Insufficient stock")

    return StockRead.model_validate(stock)


@router.post("/commit", response_model = StockRead)
async def commit_stock(
    data: StockCommitRequest,
    repo: StockRepository = Depends(get_repo)    
) -> StockRead:
    stock = await repo.commit(data.product_id, data.quantity)

    if stock is None:
        raise HTTPException(
             status_code = status.HTTP_409_CONFLICT,
             detail="Cannot commit: insufficient reserved",
        )

    return StockRead.model_validate(stock)


@router.post("/release", response_model = StockRead)
async def commit_stock(
    data: StockReserveRequest,
    repo: StockRepository = Depends(get_repo)    
) -> StockRead:
    stock = await repo.release(data.product_id, data.quantity)

    if stock is None:
        raise HTTPException(
             status_code = status.HTTP_409_CONFLICT,
             detail="Cannot release: insufficient reserved",
        )

    return StockRead.model_validate(stock)