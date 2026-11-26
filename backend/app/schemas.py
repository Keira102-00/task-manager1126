"""Pydantic 请求/响应模型（鉴权部分；任务模型在阶段3补充）。"""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class RegisterIn(BaseModel):
    """注册请求。"""
    username: str = Field(min_length=3, max_length=50, description="登录名")
    password: str = Field(min_length=6, max_length=64, description="明文密码，仅传输用，不落库")


class LoginIn(BaseModel):
    """登录请求。"""
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=64)


class UserOut(BaseModel):
    """返回给前端的用户信息（不含密码哈希）。"""
    id: int
    username: str

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    """登录成功返回的令牌。"""
    access_token: str
    token_type: str = "bearer"


# —— 任务相关 ——

# 状态枚举：前端筛选与后端校验共用同一组取值
TaskStatus = Literal["todo", "doing", "done"]


class TaskCreate(BaseModel):
    """新建任务请求。"""
    title: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: TaskStatus = "todo"


class TaskUpdate(BaseModel):
    """编辑任务请求：所有字段可选，只更新传了的字段。"""
    title: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[TaskStatus] = None


class TaskOut(BaseModel):
    """任务响应。"""
    id: int
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
