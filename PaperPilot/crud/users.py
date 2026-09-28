from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from models.users import User, UserToken
from sqlalchemy import select, update
from utils import security
from datetime import datetime, timedelta
import uuid
from schemas.users import UserUpdateInfo, UserRequest, UserChangePwdRequest


#根据用户名查询用户
async def get_user_by_username(username: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.username==username))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: User):
    # 密码加密 --> passlib
    hashed_password = security.get_password_hash(user.password)
    # 添加
    user = User(username=user.username, password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user) #从数据库读回最新的user
    return user

async def create_token(db: AsyncSession, user_id: int):
    # 1. 生成Token+ 设计过期时间 -> 查询数据库是否有Token -> 有: 更新, 没有: 新加
    token = str(uuid.uuid4())
    expires_at =datetime.now()+ timedelta(days=7) # timedelta(days=7, hours=2, minutes=30, seconds=10)

    query = select(UserToken).where(UserToken.user_id==user_id)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()

    if user_token:
        user_token.token = token
        user_token.expires_at = expires_at
        await db.commit()
    else:
        user_token = UserToken(user_id=user_id, token=token, expires_at=expires_at)
        db.add(user_token)
        await db.commit()

    return token

async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(username, db)
    if not user:
        return None
    if security.verify_password(password, user.password)==False:
        return None
    return user

# 根据Token查询用户
async def get_user_by_token(db: AsyncSession, token: str):
    query = select(UserToken).where(UserToken.token==token)
    result = await db.execute(query)
    db_token = result.scalar_one_or_none()
    if not db_token or db_token.expires_at < datetime.now():
        return None
    query = select(User).where(User.id==db_token.user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    return user


async def update_info(db: AsyncSession, username: str, user_data: UserUpdateInfo):
    # 没有设置值的不更新
    query = update(User).where(User.username==username).values(**user_data.model_dump(exclude_unset=True, exclude_none=True)) # model_dump 用于将对象转换为字典
    result = await db.execute(query)
    await db.commit()
    # 检查更新
    if result.rowcount==0:
        raise HTTPException(status_code=404, detail="User not found")
    return await get_user_by_username(username, db)


async def change_pwd(db: AsyncSession, user: User, old_pwd: str, new_pwd: str):
    if not security.verify_password(old_pwd, user.password):
        return False
    hashed_new_pwd = security.get_password_hash(new_pwd)
    user.password = hashed_new_pwd
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True




