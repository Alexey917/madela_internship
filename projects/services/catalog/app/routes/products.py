import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from redis.asyncio import Redis

from app.dependencies import get_repo, get_cache
from app.cache import get_json, set_json, delete_pattern
from app.repository import ProductRepository
from app.schemas import (
    ProductListResponse,
    ProductRead,
    ProductUpdate,
    ProductCreate
) 

router = APIRouter(prefix="/products", tags=["products"])
logger = logging.Logger(__name__)


@router.get("", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge = 1), 
    size: int = Query(20, ge = 1, le = 100), 
    repo: ProductRepository = Depends(get_repo),
    cache: Redis = Depends(get_cache),
) -> ProductListResponse:
    cache_key = f"products:page:{page}:size:{size}"

    cached = await get_json(cache_key)

    if cached is not None:
        logger.info("CACHE HIT: %s", cache_key)
        return ProductListResponse.model_validate(cached)

    logger.info("CACHE MISS: %s", cache_key)
    products, total = await repo.list(page, size)

    response = ProductListResponse(
        items=[ProductRead.model_validate(product) for product in products],
        page = page,
        size = size,
        total = total
    )

    await set_json(cache_key, response.model_dump(mode="json"), ttl=60)
    return response


@router.get("/{id}", response_model=ProductRead)
async def get_product(
    id: int, 
    repo: ProductRepository = Depends(get_repo)
) -> ProductRead | None:
    product = await repo.get(id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return ProductRead.model_validate(product)


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    repo: ProductRepository = Depends(get_repo),
    cache: Redis = Depends(get_cache),
) -> ProductRead:
    product = await repo.create(
        name = data.name,
        description = data.description,
        publisher = data.publisher,
        min_players = data.min_players,
        max_players = data.max_players,
        min_age = data.min_age,
        price = data.price,
        stock = data.stock,
        play_time_minutes = data.play_time_minutes,
    )
    await delete_pattern("products:*")
    return ProductRead.model_validate(product)


@router.put("/{id}", response_model=ProductRead)
async def update_product(
    id: int, 
    data: ProductUpdate,
    repo: ProductRepository = Depends(get_repo),
    cache: Redis = Depends(get_cache),
) -> ProductRead:
    product = await repo.update(
        id,
        name = data.name,
        description = data.description,
        publisher = data.publisher,
        min_players = data.min_players,
        max_players = data.max_players,
        min_age = data.min_age,
        price = data.price,
        stock = data.stock,
        play_time_minutes = data.play_time_minutes,
        is_active = data.is_active
    )

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    await delete_pattern("products:*")
    return ProductRead.model_validate(product)