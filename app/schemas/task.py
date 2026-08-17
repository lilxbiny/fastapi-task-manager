import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskPriority, TaskStatus


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus = TaskStatus.todo
    priority: TaskPriority | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    """Used for PUT (full update) - all fields required by the client's intent."""
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus
    priority: TaskPriority | None = None


class TaskPatch(BaseModel):
    """Used for PATCH (partial update) - every field optional."""
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None


class TaskOut(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TaskListOut(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[TaskOut]
