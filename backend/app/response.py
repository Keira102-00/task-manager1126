"""全局统一返回格式：{"code": 200, "msg": "success", "data": ...}。"""
from typing import Any


def success(data: Any = None, msg: str = "success") -> dict:
    """成功响应。"""
    return {"code": 200, "msg": msg, "data": data}


def fail(code: int, msg: str, data: Any = None) -> dict:
    """失败响应（400 / 401 / 404），由全局异常处理器统一抛出。"""
    return {"code": code, "msg": msg, "data": data}
