import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from redis.asyncio import Redis

from app.cache import delete_pattern, get_json, set_json
from app.dependencies import get_repo, get_cache
from app.repository import TaskRepository
from app.schemas import TaskCreate, TaskListResponse, TaskRead, TaskUpdate


router = APIRouter(prefix="/tasks", tags=["tasks"])
logger = logging.getLogger(__name__)


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(1, ge=1) , 
    size: int = Query(20, ge=1, le=100), 
    repo: TaskRepository = Depends(get_repo),
    cache: Redis = Depends(get_cache),
) -> TaskListResponse:
    cache_key = f"tasks:page:{page}:size:{size}"

    cached = await get_json(cache_key)
    if cached is not None:
        logger.info("CACHE HIT: %s", cache_key)
        return TaskListResponse.model_validate(cached)
    
    logger.info("CACHE MISS: %s", cache_key)
    task, total = await repo.list(page=page, size=size)

    response = TaskListResponse(
        items=[TaskRead.model_validate(t) for t in task],
        total=total,
        page=page,
        size=size
    )

    await set_json(cache_key, response.model_dump(mode="json"), ttl=60)
    return response


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
    repo: TaskRepository = Depends(get_repo),
    cache: Redis = Depends(get_cache),
) -> TaskRead:
    task = await repo.create(title=data.title, description=data.description)
    await delete_pattern("tasks:*")
    return TaskRead.model_validate(task)


@router.put("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int, 
    data: TaskUpdate,
    repo: TaskRepository = Depends(get_repo),
    cache: Redis = Depends(get_cache),
) -> TaskRead:
    task = await repo.update(
        task_id=task_id,
        title=data.title,
        description=data.description,
        is_done=data.is_done
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    await delete_pattern("tasks:*")
    return TaskRead.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int, 
    repo: TaskRepository = Depends(get_repo),
    cache: Redis = Depends(get_cache),
) -> None:
    deleted = await repo.delete(task_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Task not found")
    await delete_pattern("tasks:*")
    