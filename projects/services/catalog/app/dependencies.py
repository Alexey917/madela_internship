from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.repository import ProductRepository
from app.cache import redis_client


async def get_repo(
    session: AsyncSession = Depends(get_session)
) -> AsyncGenerator[ProductRepository, None]:
    yield ProductRepository(session)


def get_cache():
    return redis_client