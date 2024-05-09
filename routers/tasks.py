from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from services.tasks import TaskService
from repository.task_repository import TaskRepository
from configs.database import get_session
from schemas.tasks import (
    TaskCountResponse,
    TaskResponse,
    AddTaskRequest,
    MultiTaskResponse,
    AddMultipleTasksRequest,
    DeleteTaskRequest,
    DeleteTaskResponse,
    CompleteTaskRequest,
    CompleteTaskResponse,
)

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)


@router.get("/", response_model=TaskCountResponse)
async def get_tasks(user_id: int, db: AsyncSession = Depends(get_session)):
    service = TaskService(TaskRepository(db), user_id)
    try:
        return await service.get_tasks_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=TaskResponse)
async def add_task(request: AddTaskRequest, db: AsyncSession = Depends(get_session)):
    service = TaskService(TaskRepository(db), request.user_id)
    return await service.add_task(request.description)

@router.post("/multiple", response_model=MultiTaskResponse)
async def add_multiple_tasks(request: AddMultipleTasksRequest, db: AsyncSession = Depends(get_session)):
    service = TaskService(TaskRepository(db), request.user_id)
    try:
        tasks = await service.add_multiple_tasks(request.descriptions)
        return {"tasks": tasks}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{task_id}", response_model=DeleteTaskResponse)
async def delete_task(request: DeleteTaskRequest, db: AsyncSession = Depends(get_session)):
    service = TaskService(TaskRepository(db), request.user_id)
    try:
        success = await service.remove_task(request.task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"message": "Task deleted"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/complete/{task_id}", response_model=CompleteTaskResponse)
async def complete_task(request: CompleteTaskRequest, db: AsyncSession = Depends(get_session)):
    service = TaskService(TaskRepository(db), request.user_id)
    try:
        task = await service.complete_task(request.task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))