import asyncio

from app.db import SessionLocal
from app.repository import TaskRepository


async def main() -> None:
    async with SessionLocal() as session:
        repo = TaskRepository(session)

        # create
        task = await repo.create(title="Купить хлеб", description="Не забыть")
        print(f"Created: id={task.id}, title={task.title}, created_at={task.created_at}")

        # get
        fetched = await repo.get(task.id)
        print(f"Fetched: {fetched}")

        # update
        updated = await repo.update(task.id, is_done=True)
        print(f"Updated: is_done={updated.is_done}, updated_at={updated.updated_at}")

        # list
        tasks, total = await repo.list(page=1, size=10)
        print(f"List: total={total}, items={[t.title for t in tasks]}")

        # delete
        deleted = await repo.delete(task.id)
        print(f"Deleted: {deleted}")

        # get после delete
        missing = await repo.get(task.id)
        print(f"After delete: {missing}")


if __name__ == "__main__":
    asyncio.run(main())