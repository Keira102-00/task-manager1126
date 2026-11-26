"""FastAPI 入口：应用实例、CORS、全局异常处理、建表。"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

from app.database import engine, Base
from app.response import fail
from app.routers import auth, tasks

# 建表：启动时自动创建尚未存在的表（生产环境应换成 Alembic 迁移，面试可作为待优化点）
Base.metadata.create_all(bind=engine)

app = FastAPI(title="轻量任务管理系统")

# 前后端分离开发跨域：仅放行本地前端地址
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """把 FastAPI 抛出的 HTTPException 转成统一返回格式。"""
    return JSONResponse(
        status_code=exc.status_code,
        content=fail(code=exc.status_code, msg=str(exc.detail)),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """入参校验失败：统一成 400，取第一条错误信息提示前端。"""
    first = exc.errors()[0] if exc.errors() else {}
    msg = f"参数错误：{first.get('msg', '非法入参')}"
    return JSONResponse(status_code=400, content=fail(code=400, msg=msg))


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """兜底异常：不把内部错误细节暴露给前端。"""
    return JSONResponse(status_code=500, content=fail(code=500, msg="服务器内部错误"))


# 路由在后续阶段挂载：app.include_router(...)
app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/")
def health_check():
    return {"code": 200, "msg": "success", "data": {"status": "ok"}}
