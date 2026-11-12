from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.repository import OrderRepository
from app.saga import SagaService


async def get_repo(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[OrderRepository, None]:
    yield OrderRepository(session)


async def get_saga(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[SagaService, None]:
    yield SagaService(session)