from datetime import datetime
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from models.TaskModel import Task
from models.TaskCount import TaskCounter
from sqlalchemy.future import select
from sqlalchemy import func


async def create_tasks(descriptions: List[str], user_id: int, db: AsyncSession):
    task_counter = await db.scalar(
        select(TaskCounter).where(TaskCounter.user_id == user_id)
    )
    if not task_counter:
        task_counter = TaskCounter(user_id=user_id, total_created=0, total_completed=0)
        db.add(task_counter)
        await db.commit()

    current_active_count = await db.scalar(
        select(func.count())
        .select_from(Task)
        .where(Task.user_id == user_id, Task.completed == False)
    )
    available_slots = 10 - current_active_count

    tasks_to_complete = len(descriptions) - available_slots
    if tasks_to_complete > 0:
        oldest_tasks = await db.execute(
            select(Task)
            .where(Task.user_id == user_id, Task.completed == False)
            .order_by(Task.created_at)
            .limit(tasks_to_complete)
        )
        for task in oldest_tasks.scalars().all():
            task.completed = True
            task_counter.total_completed += 1

    tasks = []
    for description in descriptions:
        task = Task(
            user_id=user_id,
            description=description,
            created_at=datetime.now(),
            completed=False,
        )
        db.add(task)
        tasks.append(task)

    task_counter.total_created += len(descriptions)
    await db.commit()

    if len(tasks) == 1:
        return tasks[0]
    else:
        return tasks
