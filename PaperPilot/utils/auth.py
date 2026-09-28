from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from config.db_conf import get_database

from crud import users
# 整合 根据Token 查询用户信息
async def get_current_user(authorization: str = Header(..., alias="Authorization"), db: AsyncSession=Depends(get_database)):
    # token = authorization.split(" ")[1]
    token = authorization.replace("Bearer ", "")
    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status=status.HTTP_401_UNAUTHORIZED, detail="令牌不存在或过期")
    return user