from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class UserRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="用户密码")

class UserInfoBase(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个⼈简介")
# user_info 对应的类
class UserInfoRespone(UserInfoBase):
    id: int
    username: str
    model_config = ConfigDict(from_attributes=True)

# data 有自己的数据类型
class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoRespone = Field(..., alias="userInfo")  # 定义的类

    #模型类配置
    model_config = ConfigDict(
        populate_by_name=True, # alias 和字段名兼容
        from_attributes=True # 允许从ORM 模型中获取数据
    )

class UserUpdateInfo(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个⼈简介")
    phone: Optional[str] = Field(None, max_length= 12, description="个人手机号")

class UserChangePwdRequest(BaseModel):
    old_password: str = Field(..., alias="oldPassword", description="旧密码")
    new_password : str = Field(..., alias="newPassword", max_length=6 ,description="新密码")