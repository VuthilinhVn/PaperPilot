from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import UniqueConstraint, Index, Integer, String, DateTime, ForeignKey
from datetime import datetime
from models.users import User
from models.papers import PapersList

class Base(DeclarativeBase):
    pass

class PaperBrowserHistory(Base):
    __tablename__ = "history"

    __table_args__ = (
        # UniqueConstraint: 唯一, 当前用户只能收藏当前论文一次
        UniqueConstraint("user_id", "paper_id", name="unique_history"),
        Index("fk_history_user_idx", "user_id"),
        Index("fk_history_papers_idx", "paper_id")
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False, comment="ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id), nullable=False, comment="用户ID")
    paper_id: Mapped[int] = mapped_column(Integer, ForeignKey(PapersList.id), nullable=False, comment="论文ID")
    view_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


    def __repr__(self):
        return f"<History(id={self.id}, user_id={self.user_id}, papers_id={self.paper_id}, created_at={self.view_time}>"