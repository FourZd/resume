from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from services.tasks import create_tasks
from configs.database import get_session
from models.TaskModel import Task
from schemas.tasks import (
    TaskRequest,
    TaskCount,
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


@router.get("/", response_model=TaskCount)
async def get_tasks(user_id: int = Query(..., description="The ID of the user to retrieve tasks for"), db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Task).where(Task.user_id == user_id, Task.completed == False))
    active_tasks = result.scalars().all()
    created_count = await db.scalar(select(func.count()).select_from(select(Task).where(Task.user_id == user_id)))
    active_count = await db.scalar(select(func.count()).select_from(select(Task).where(Task.user_id == user_id, Task.completed == False)))
    completed_count = await db.scalar(select(func.count()).select_from(select(Task).where(Task.user_id == user_id, Task.completed == True)))
    return {"active_tasks": active_tasks, "created_count": created_count, "active_count": active_count, "completed_count": completed_count}


@router.post("/", response_model=TaskResponse)
async def add_task(request: AddTaskRequest, db: AsyncSession = Depends(get_session)):
    return await create_tasks([request.description], request.user_id, db)


@router.post("/multiple", response_model=MultiTaskResponse)
async def add_multiple_tasks(
    request: AddMultipleTasksRequest, db: AsyncSession = Depends(get_session)
):
    if len(request.descriptions) != 5:
        raise HTTPException(
            status_code=400, detail="Exactly 5 descriptions required")
    return {"tasks": await create_tasks(request.descriptions, request.user_id, db)}


@router.delete("/{task_id}", response_model=DeleteTaskResponse)
async def delete_task(
    request: DeleteTaskRequest, db: AsyncSession = Depends(get_session)
):
    task = await db.get(Task, request.task_id)
    if task and task.user_id == request.user_id:
        await db.delete(task)
        await db.commit()
        return {"message": "Task deleted"}
    else:
        raise HTTPException(
            status_code=404, detail="Task not found or not owned by user"
        )


@router.put("/complete/{task_id}", response_model=CompleteTaskResponse)
async def complete_task(
    request: CompleteTaskRequest, db: AsyncSession = Depends(get_session)
):
    task = await db.get(Task, request.task_id)
    if task and task.user_id == request.user_id:
        task.completed = True
        await db.commit()
        return task
    else:
        raise HTTPException(
            status_code=404, detail="Task not found or not owned by user"
        )
