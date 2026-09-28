from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import UniqueConstraint, Index, Integer, String, DateTime, ForeignKey
from datetime import datetime
from models import users, papers

class Base(DeclarativeBase):
    pass

class Favorite(Base):
    __tablename__ = "favorite"

    __table_args__ = (
        # UniqueConstraint: 唯一, 当前用户只能收藏当前论文一次
        UniqueConstraint("user_id", "paper_id", name="unique_favorite"),
        Index("fk_favorite_user_idx", "user_id"),
        Index("fk_favorite_papers_idx", "paper_id")
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False, comment="ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(users.User.id), nullable=False, comment="用户ID")
    paper_id: Mapped[int] = mapped_column(Integer, ForeignKey(papers.PapersList.id), nullable=False, comment="论文ID")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")

    def __repr__(self):
        return f"<Favorite(id={self.id}, user_id={self.user_id}, papers_id={self.paper_id}, created_at={self.created_at}>"