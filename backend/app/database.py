"""数据库连接与会话：SQLite + SQLAlchemy。"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite 文件路径，相对后端启动目录
DATABASE_URL = "sqlite:///./task.db"

# check_same_thread=False：SQLite 多线程下的必要配置（FastAPI 多线程请求）
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 会话工厂：autocommit 关闭，由代码显式 commit / rollback
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 所有模型继承的基类
Base = declarative_base()


def get_db():
    """依赖注入：每个请求拿一个独立会话，结束后关闭。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
