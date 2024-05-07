from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from services.tasks import create_tasks
from configs.database import get_session
from models.TaskModel import Task
from models.TaskCount import TaskCounter
from schemas.tasks import (
    TaskRequest,
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
    active_tasks = None
    task_counter = await db.scalar(
        select(TaskCounter).where(TaskCounter.user_id == user_id)
    )
    if not task_counter:
        all_tasks_result = await db.execute(
            select(Task).where(Task.user_id == user_id)
        )
        all_tasks = all_tasks_result.scalars().all()
        active_tasks = [task for task in all_tasks if not task.completed]
        completed_tasks = [task for task in all_tasks if task.completed]
        
        task_counter = TaskCounter(
            user_id=user_id,
            total_created=len(all_tasks),  
            total_completed=len(completed_tasks) 
        )
        db.add(task_counter)
        await db.commit()

    if not active_tasks:
        active_tasks = await db.execute(
            select(Task).where(Task.user_id == user_id, Task.completed == False)
        )
        active_tasks = active_tasks.scalars().all()
    return {
        "active_tasks": active_tasks,
        "created_count": task_counter.total_created,
        "completed_count": task_counter.total_completed,
    }


@router.post("/", response_model=TaskResponse)
async def add_task(request: AddTaskRequest, db: AsyncSession = Depends(get_session)):
    return await create_tasks([request.description], request.user_id, db)


@router.post("/multiple", response_model=MultiTaskResponse)
async def add_multiple_tasks(
    request: AddMultipleTasksRequest, db: AsyncSession = Depends(get_session)
):
    if len(request.descriptions) != 5:
        raise HTTPException(status_code=400, detail="Exactly 5 descriptions required")
    return {"tasks": await create_tasks(request.descriptions, request.user_id, db)}


@router.delete("/{task_id}", response_model=DeleteTaskResponse)
async def delete_task(
    request: DeleteTaskRequest, db: AsyncSession = Depends(get_session)
):
    task = await db.get(Task, request.task_id)
    if task and task.user_id == request.user_id:
        await db.delete(task)
        task_counter = await db.scalar(
            select(TaskCounter).where(TaskCounter.user_id == request.user_id)
        )
        task_counter.total_created -= 1
        if task.completed:
            task_counter.total_completed -= 1
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
        task_counter = await db.scalar(
            select(TaskCounter).where(TaskCounter.user_id == request.user_id)
        )
        task_counter.total_completed += 1
        await db.commit()
        return task
    else:
        raise HTTPException(
            status_code=404, detail="Task not found or not owned by user"
        )
