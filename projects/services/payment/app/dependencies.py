from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends
from app.repository import PaymentRepository
from app.db import get_session

async def get_repo(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[PaymentRepository, None]:
    yield PaymentRepository(session)