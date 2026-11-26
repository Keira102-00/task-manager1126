"""公共依赖：从请求头解析 JWT，拿到当前登录用户。"""
import jwt
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import decode_access_token


def get_current_user(
    authorization: str = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    """校验令牌并返回当前用户；任何失败统一 401。"""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录或登录已过期"
    )

    # 手动解析 Authorization: Bearer <token>，未带/格式错误都按 401 处理
    if not authorization or not authorization.startswith("Bearer "):
        raise unauthorized
    token = authorization.split(" ", 1)[1].strip()

    try:
        user_id = decode_access_token(token)
    except jwt.PyJWTError:
        raise unauthorized

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise unauthorized
    return user
