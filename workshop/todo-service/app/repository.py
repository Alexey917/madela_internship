from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task

class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self, page: int=1, size: int=20) -> tuple[list[Task], int]:
        """Возвращает (список задач на странице, всего задач)."""
        offset = (page - 1) * size

        # Общее количество
        total_result = await self.session.execute(select(func.count()).select_from(Task))
        total = total_result.scalar_one()

        # Список с пагинацией
        result = await self.session.execute(select(Task).order_by(Task.id).offset(offset).limit(size))
        tasks = list(result.scalars().all())

        return tasks, total


    async def get(self, task_id: int) -> Task | None:
        result = await  self.session.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()


    async def create(self, title: str, description: str | None = None) -> Task:
        task = Task(title=title, description=description)
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task


    async def update(
        self, 
        task_id: int, 
        title: str | None = None, 
        is_done: bool | None = None, 
        description: str | None = None
    ) -> Task | None:
        task = await self.get(task_id)
        if task is None:
            return None

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if is_done is not None:
            task.is_done = is_done

        await self.session.commit()
        await self.session.refresh(task)
        return task


    async def delete(self, task_id: int) -> bool:
        task = await self.get(task_id)
        if task is None:
            return False

        await self.session.commit()
        await self.session.refresh(task)
        return True

        
        