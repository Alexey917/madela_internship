from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_repo
from app.repository import TaskRepository
from app.schemas import TaskCreate, TaskListResponse, TaskRead, TaskUpdate


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(1, ge=1) , 
    size: int = Query(20, ge=1, le=100), 
    repo: TaskRepository = Depends(get_repo)
) -> TaskListResponse:
    task, total = await repo.list(page=page, size=size)
    return TaskListResponse(
        items=[TaskRead.model_validate(t) for t in task],
        total=total,
        page=page,
        size=size
    )


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int, 
    repo: TaskRepository = Depends(get_repo)
) -> TaskRead:
    task = await repo.get(task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskRead.model_validate(task)


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    repo: TaskRepository = Depends(get_repo)
) -> TaskRead:
    task = await repo.create(title=data.title, description=data.description)
    return TaskRead.model_validate(task)


@router.put("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int, 
    data: TaskUpdate,
    repo: TaskRepository = Depends(get_repo)
) -> TaskRead:
    task = await repo.update(
        task_id=task_id,
        title=data.title,
        description=data.description,
        is_done=data.is_done
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskRead.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int, 
    repo: TaskRepository = Depends(get_repo)
) -> None:
    deleted = await repo.delete(task_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Task not found")
    