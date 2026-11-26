"""ORM 模型：仅 user、task 两张表。"""
from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # 登录名，唯一索引，注册时查重
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    # 只存 bcrypt 哈希，禁止存明文（哈希逻辑在鉴权模块实现）
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 反向关系：一个用户有多条任务，级联删除可选
    tasks: Mapped[list["Task"]] = relationship(back_populates="user")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 状态：todo / doing / done，筛选时按此字段过滤
    status: Mapped[str] = mapped_column(String(20), default="todo", nullable=False)
    # 外键指向用户；数据隔离的核心：查询时必须带 user_id
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user: Mapped[User] = relationship(back_populates="tasks")
