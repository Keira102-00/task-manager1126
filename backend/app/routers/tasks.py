"""任务路由：CRUD + status 筛选；所有查询强制带 user_id，实现数据隔离。"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Task, User
from app.deps import get_current_user
from app.schemas import TaskCreate, TaskUpdate, TaskOut, TaskStatus
from app.response import success

router = APIRouter(prefix="/tasks", tags=["任务"])


def _get_owned_task(db: Session, task_id: int, current_user: User) -> Task:
    """按 id + user_id 双条件查任务；查不到统一 404，不区分"不存在"还是"属于他人"。"""
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.user_id == current_user.id)
        .first()
    )
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在或无权访问")
    return task


@router.get("")
def list_tasks(
    status: Optional[TaskStatus] = Query(default=None, description="按状态筛选，不传则返回全部"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """当前用户的任务列表，可按 status 过滤，最新创建在前。"""
    query = db.query(Task).filter(Task.user_id == current_user.id)
    if status:
        query = query.filter(Task.status == status)
    tasks = query.order_by(Task.created_at.desc()).all()
    return success(data=[TaskOut.model_validate(t).model_dump() for t in tasks])


@router.get("/{task_id}")
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """查询单条任务。"""
    task = _get_owned_task(db, task_id, current_user)
    return success(data=TaskOut.model_validate(task).model_dump())


@router.post("")
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """新建任务，user_id 取自登录用户，不接受前端传入。"""
    task = Task(**payload.model_dump(), user_id=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return success(data=TaskOut.model_validate(task).model_dump(), msg="创建成功")


@router.put("/{task_id}")
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """编辑任务：只更新请求里传了的字段。"""
    task = _get_owned_task(db, task_id, current_user)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return success(data=TaskOut.model_validate(task).model_dump(), msg="更新成功")


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除任务。"""
    task = _get_owned_task(db, task_id, current_user)
    db.delete(task)
    db.commit()
    return success(msg="删除成功")
