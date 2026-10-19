from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.repository import ProductRepository


async def get_repo(
    session: AsyncSession = Depends(get_session)
) -> AsyncGenerator[ProductRepository, None]:
    yield ProductRepository(session)
