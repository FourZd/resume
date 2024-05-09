from repository.task_repository import TaskRepository
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List


class TaskService:
    def __init__(self, repository: TaskRepository, user_id: int):
        self.repository = repository
        self.user_id = user_id

    async def get_tasks_summary(self):
        task_counter = await self.repository.get_task_counter(self.user_id)
        active_tasks = await self.repository.get_active_tasks(self.user_id)
        return {
            "active_tasks": active_tasks,
            "created_count": task_counter.total_created if task_counter else 0,
            "completed_count": task_counter.total_completed if task_counter else 0
        }

    async def add_task(self, description: str):
        task = await self.repository.create_tasks(self.user_id, [description])
        await self.repository.update_or_create_counter(self.user_id, created_increment=1)
        return task

    async def add_multiple_tasks(self, descriptions: List[str]):
        if len(descriptions) != 5:
            raise ValueError("Exactly 5 descriptions are required")
        tasks = await self.repository.create_tasks(self.user_id, descriptions)
        await self.repository.update_or_create_counter(self.user_id, created_increment=len(descriptions))
        return tasks

    async def complete_task(self, task_id: int):
        task = await self.repository.update_task_completion(task_id, self.user_id)
        if task:
            await self.repository.update_or_create_counter(self.user_id, completed_increment=1)
        return task

    async def remove_task(self, task_id: int):
        success, is_task_completed = await self.repository.delete_task(task_id, self.user_id)
        if success:
            await self.repository.update_or_create_counter(self.user_id, created_increment=-1, completed_increment=-1 if is_task_completed else 0)
        return success


async def get_task_service(db: AsyncSession, user_id: int) -> TaskService:
    repository = TaskRepository(db)
    return TaskService(repository, user_id)
