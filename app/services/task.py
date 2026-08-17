import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskPatch, TaskUpdate


def create_task(db: Session, owner_id: uuid.UUID, task_in: TaskCreate) -> Task:
    task = Task(**task_in.model_dump(), owner_id=owner_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_owned_task_or_404(db: Session, task_id: uuid.UUID, owner_id: uuid.UUID) -> Task:
    """
    Fetch a task, scoped to its owner.

    We deliberately return 404 (not 403) for tasks that belong to someone
    else, so we don't leak the existence of other users' task IDs.
    """
    task = db.get(Task, task_id)
    if task is None or task.owner_id != owner_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


def list_tasks(
    db: Session,
    owner_id: uuid.UUID,
    skip: int = 0,
    limit: int = 20,
    status_filter: TaskStatus | None = None,
) -> tuple[list[Task], int]:
    query = select(Task).where(Task.owner_id == owner_id)
    count_query = select(func.count()).select_from(Task).where(Task.owner_id == owner_id)

    if status_filter is not None:
        query = query.where(Task.status == status_filter)
        count_query = count_query.where(Task.status == status_filter)

    total = db.scalar(count_query) or 0

    query = query.order_by(Task.created_at.desc()).offset(skip).limit(limit)
    items = list(db.scalars(query).all())
    return items, total


def full_update_task(db: Session, task: Task, task_in: TaskUpdate) -> Task:
    for field, value in task_in.model_dump().items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def partial_update_task(db: Session, task: Task, task_in: TaskPatch) -> Task:
    for field, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()
