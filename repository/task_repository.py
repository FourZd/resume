from sqlalchemy.ext.asyncio import AsyncSession
from models.TaskModel import Task
from models.TaskCount import TaskCounter
from sqlalchemy.future import select
from datetime import datetime
from typing import List


class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_task(self, user_id: int, description: str):
        task = Task(user_id=user_id, description=description, created_at=datetime.now(), completed=False)
        self.db.add(task)
        await self.db.commit()
        return task

    async def create_tasks(self, user_id: int, descriptions: List[str]):
        tasks = [Task(user_id=user_id, description=desc, created_at=datetime.now(), completed=False) for desc in descriptions]
        self.db.add_all(tasks)
        await self.db.commit()
        return tasks
    
    async def get_active_tasks(self, user_id: int):
        result = await self.db.execute(select(Task).where(Task.user_id == user_id, Task.completed == False))
        return result.scalars().all()
    
    async def get_task_counter(self, user_id: int):
        return await self.db.scalar(
            select(TaskCounter).where(TaskCounter.user_id == user_id)
        )
    
    async def update_task_completion(self, task_id: int, user_id: int):
        task = await self.db.get(Task, task_id)
        if task and task.user_id == user_id:
            task.completed = True
            await self.db.commit()
            return task
        return None

    async def update_or_create_counter(self, user_id: int, created_increment=0, completed_increment=0):
        counter = await self.get_task_counter(user_id)
        if not counter:
            counter = TaskCounter(user_id=user_id, total_created=0, total_completed=0)
            self.db.add(counter)
        counter.total_created += created_increment
        counter.total_completed += completed_increment
        await self.db.commit()
        return counter
    
    async def delete_task(self, task_id: int, user_id: int):
        task = await self.db.get(Task, task_id)
        if task and task.user_id == user_id:
            is_task_completed = task.completed
            await self.db.delete(task)
            await self.db.commit()
            return True, is_task_completed
        return False, None
    