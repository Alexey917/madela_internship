from collections.abc import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository import StockRepository
from app.db import get_session

async def get_repo(
    session: AsyncSession = Depends(get_session)
) -> AsyncGenerator[StockRepository, None]:
    yield StockRepository(session)