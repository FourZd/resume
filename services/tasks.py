from datetime import datetime
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from models.TaskModel import Task
from sqlalchemy.future import select
from sqlalchemy import func


async def create_tasks(descriptions: List[str], user_id: int, db: AsyncSession):
    current_task_count = await db.execute(
        select(func.count())
        .select_from(Task)
        .where(Task.user_id == user_id, Task.completed == False)
    )
    current_task_count = current_task_count.scalar()

    available_slots = 10 - current_task_count
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
        await db.commit()

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
    await db.commit()

    if len(tasks) == 1:
        return tasks[0]
    else:
        return tasks
