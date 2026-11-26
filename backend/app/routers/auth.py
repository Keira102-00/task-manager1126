"""鉴权路由：注册、登录。"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import RegisterIn, LoginIn, UserOut, TokenOut
from app.security import hash_password, verify_password, create_access_token
from app.response import success

router = APIRouter(prefix="/auth", tags=["鉴权"])


@router.post("/register")
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    """注册：用户名查重后写入 bcrypt 哈希，不返回密码。"""
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")

    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return success(data=UserOut.model_validate(user).model_dump())


@router.post("/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    """登录：校验通过后签发 JWT。"""
    user = db.query(User).filter(User.username == payload.username).first()

    # 用户不存在或密码错误，返回同样的提示，避免枚举用户名
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    token = create_access_token(user.id)
    return success(data=TokenOut(access_token=token).model_dump())
