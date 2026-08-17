import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models.task import TaskStatus
from app.models.user import User
from app.schemas.task import TaskCreate, TaskListOut, TaskOut, TaskPatch, TaskUpdate
from app.services.task import (
    create_task,
    delete_task,
    full_update_task,
    get_owned_task_or_404,
    list_tasks,
    partial_update_task,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_task(db, owner_id=current_user.id, task_in=task_in)


@router.get("/", response_model=TaskListOut)
def list_my_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: TaskStatus | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = list_tasks(
        db, owner_id=current_user.id, skip=skip, limit=limit, status_filter=status_filter
    )
    return TaskListOut(total=total, skip=skip, limit=limit, items=items)


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_owned_task_or_404(db, task_id, current_user.id)


@router.put("/{task_id}", response_model=TaskOut)
def update_task_full(
    task_id: uuid.UUID,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_owned_task_or_404(db, task_id, current_user.id)
    return full_update_task(db, task, task_in)


@router.patch("/{task_id}", response_model=TaskOut)
def update_task_partial(
    task_id: uuid.UUID,
    task_in: TaskPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_owned_task_or_404(db, task_id, current_user.id)
    return partial_update_task(db, task, task_in)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_task(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_owned_task_or_404(db, task_id, current_user.id)
    delete_task(db, task)
    return None
