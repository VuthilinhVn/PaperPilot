from sqlalchemy import Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from typing import Optional
from sqlalchemy import Index

class Base(DeclarativeBase):
    pass

#密码要加密, 加密方法为bcrypt
class User(Base):
    __tablename__ = "user"

    # 用户因素=> 企业项目->创建查询效率更高, 因为数据高频查询
    __table_args__ = (
        Index("username_UNIQUE", "username"),
        Index("phone_UNIQUE", "phone")
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False ,comment="用户ID")
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, comment="用户名")
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment="用户密码")
    nickname: Mapped[Optional[str]] = mapped_column(String(50), comment="用户昵称")
    avatar: Mapped[str] = mapped_column(String(255), comment="用户头像URL", default="https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg")
    gender: Mapped[Optional[str]] = mapped_column(Enum("male", "female", "unknown"), comment="用户性别")
    bio: Mapped[str] = mapped_column(String(255), comment="用户简介")
    phone: Mapped[str] = mapped_column(String(20), comment="用户手机")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', nickname='{self.nickname}')>"

class UserToken(Base):
    __tablename__ = "user_token"

    __table_args__ = (
        Index("token_UNIQUE", "token"),
        Index("fk_user_token_user_idx", "user_id")
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id), nullable=False)
    token: Mapped[str] = mapped_column(String(255), comment="Token")
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="过期时间")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")

    def __repr__(self):
        return f"<UserToken(id={self.user_id}, token='{self.token}')>"