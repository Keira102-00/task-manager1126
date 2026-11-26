"""安全工具：bcrypt 密码哈希 + JWT 签发/解析。"""
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

# —— JWT 配置（轻量项目先写常量；生产环境应放到环境变量）——
SECRET_KEY = "change-me-to-a-random-secret-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

# bcrypt 哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """明文 -> bcrypt 哈希。"""
    return pwd_context.hash(plain)


def verify_password(plain: str, password_hash: str) -> bool:
    """校验明文密码是否与哈希匹配。"""
    return pwd_context.verify(plain, password_hash)


def create_access_token(user_id: int) -> str:
    """签发 JWT，payload 中只放用户 id 和过期时间。"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int:
    """解析 JWT，返回用户 id；无效/过期则抛异常，由依赖层转成 401。"""
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    # sub 为用户 id 字符串
    return int(payload["sub"])
