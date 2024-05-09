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
        await self._manage_old_tasks(self.user_id)
        task = await self.repository.create_tasks(self.user_id, [description])
        task = task[0]
        await self.repository.update_or_create_counter(self.user_id, created_increment=1)
        await self.repository.commit_changes()
        return task

    async def add_multiple_tasks(self, descriptions: List[str]):
        if len(descriptions) != 5:
            raise ValueError("Exactly 5 descriptions are required")
        await self._manage_old_tasks(self.user_id, new_tasks_count=len(descriptions))
        tasks = await self.repository.create_tasks(self.user_id, descriptions)
        await self.repository.update_or_create_counter(self.user_id, created_increment=len(descriptions))
        await self.repository.commit_changes()
        return tasks

    async def complete_task(self, task_id: int):
        task = await self.repository.update_tasks_completion([task_id], self.user_id)
        if task:
            await self.repository.update_or_create_counter(self.user_id, completed_increment=1)
            await self.repository.commit_changes()
        return task

    async def remove_task(self, task_id: int):
        success, is_task_completed = await self.repository.delete_task(task_id, self.user_id)
        if success:
            await self.repository.update_or_create_counter(self.user_id, created_increment=-1, completed_increment=-1 if is_task_completed else 0)
            await self.repository.commit_changes()
        return success

    async def _manage_old_tasks(self, user_id: int, new_tasks_count=1):
        active_tasks = await self.repository.get_active_tasks(user_id)
        print(f"Active tasks: {active_tasks}")
        tasks_to_complete = len(active_tasks) + new_tasks_count - 10
        print(f"Tasks to complete: {tasks_to_complete}")
        if tasks_to_complete > 0:
            print(f"Completing {tasks_to_complete} tasks")
            tasks_to_update = sorted(active_tasks, key=lambda x: x.created_at)[:tasks_to_complete]
            print(f"Tasks to update: {tasks_to_update}")
            task_ids_to_update = [task.id for task in tasks_to_update]
            print(f"Task IDs to update: {task_ids_to_update}")

            if task_ids_to_update:
                await self.repository.update_tasks_completion(task_ids_to_update, user_id)
            await self.repository.update_or_create_counter(user_id, completed_increment=tasks_to_complete)

async def get_task_service(db: AsyncSession, user_id: int) -> TaskService:
    repository = TaskRepository(db)
    return TaskService(repository, user_id)
