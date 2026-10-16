from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.repository import TaskRepository


async def get_repo(session: AsyncSession = Depends(get_session)) -> AsyncGenerator[TaskRepository, None]:
    yield TaskRepository(session)

