from pydantic import BaseModel
from datetime import datetime
from typing import List


class Task(BaseModel):
    id: int
    user_id: int
    description: str
    created_at: datetime
    completed: bool = False


class TaskRequest(BaseModel):
    user_id: int


class TaskCountResponse(BaseModel):
    active_tasks: List[Task]
    created_count: int
    completed_count: int


class AddTaskRequest(BaseModel):
    description: str
    user_id: int


class TaskResponse(BaseModel):
    id: int
    user_id: int
    description: str
    created_at: datetime
    completed: bool


class AddMultipleTasksRequest(BaseModel):
    descriptions: List[str]
    user_id: int


class MultiTaskResponse(BaseModel):
    tasks: List[TaskResponse]


class DeleteTaskRequest(BaseModel):
    task_id: int
    user_id: int


class DeleteTaskResponse(BaseModel):
    message: str


class CompleteTaskRequest(BaseModel):
    task_id: int
    user_id: int


class CompleteTaskResponse(TaskResponse):
    pass
