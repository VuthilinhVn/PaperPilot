from fastapi import APIRouter, Depends, HTTPException, Header
from config.db_conf import get_database
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.users import UserRequest, UserInfoRespone, UserAuthResponse, UserUpdateInfo, UserChangePwdRequest
from crud import users
from utils.response import success_response
from utils.auth import get_current_user
from models.users import User
router = APIRouter(prefix="/api/user", tags=["users"])


@router.post("/register")
async def register(user_data: UserRequest,db: AsyncSession = Depends(get_database)):
    # 1. 验证用户是否存在, 如果存在则返回错误
    if await users.get_user_by_username(user_data.username, db) is not None:
        raise HTTPException(status_code=400, detail="用户已存在")
    # 2. 创建用户
    user = await users.create_user(db, user_data)
    # 3. 生成token: Token 用来判断用户是否登录-> 可以看并修改个人信息
    token = await users.create_token(db, user.id)

#     return {
#   "code": 200,
#   "message": "注册成功",
#   "data": {
#     "token": token,
#     "userInfo": {
#       "id": user.id,
#       "username": user.username,
#       "bio": user.bio,
#       "avatar": user.avatar
#     }
#   }
# }
    response_data = UserAuthResponse(token=token, user_info=UserInfoRespone.model_validate(user))
    return success_response(data=response_data)


@router.post("/login")
async def login_user(login_data: UserRequest, db: AsyncSession = Depends(get_database)):
    user = await users.authenticate_user(db, login_data.username, login_data.password)
    if user is None:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = await users.create_token(db, user.id)
    response_data = UserAuthResponse(token=token, user_info=UserInfoRespone.model_validate(user))
    return success_response(message="登录成功", data=response_data)

@router.get("/info")
async def get_user_info(user: User= Depends(get_current_user)):
    return success_response(message="获取用户信息成功", data=UserInfoRespone.model_validate(user))

@router.put("/update") # 先验证Token, 用户输入更新信息, 响应结果
async def update_user_info(user_data: UserUpdateInfo, user: User=Depends(get_current_user), db: AsyncSession=Depends(get_database)):
    user = await users.update_info(db, user.username, user_data)
    return success_response(message="更新用户信息成功", data=UserInfoRespone.model_validate(user))

@router.put("/password")
async def update_password(user_data: UserChangePwdRequest, user: User=Depends(get_current_user), db: AsyncSession=Depends(get_database)):
    result = await users.change_pwd(db, user, user_data.old_password, user_data.new_password)
    if not result:
        raise HTTPException(status_code=400, detail="旧密码错误")
    return success_response(message="更新密码成功")