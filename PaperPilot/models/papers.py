from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, ForeignKey, Index
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Categories(Base):
    __tablename__ = "paper_primary_category"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False, comment="主键ID")
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="分类名称")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, comment="排序")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment="更新时间")


class PapersList(Base):
    __tablename__ = "papers"

    # 创建索引: 提升查询速度 -> 添加目录
    __table_args__ = (
        Index("fk_papers_category_idx", "category_id"),
        Index("idx_submitted_time", "submitted_at")
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="ID")
    paper_id: Mapped[str] = mapped_column(String(255), nullable=False, comment="论文ID")
    title: Mapped[str] = mapped_column(String(500), nullable=False, comment="论文标题")
    abstract: Mapped[str] = mapped_column(String(255), comment="论文摘要")
    first_author: Mapped[str] = mapped_column(String(50), comment="作者")
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('paper_primary_category.id'),nullable=False, comment="分类ID")
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, comment="发布时间")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment="更新时间")
    pdf_url: Mapped[str] = mapped_column(String(255), comment="PDF URL")
    arxiv_url: Mapped[str] = mapped_column(String(255), comment="ArXiv URL")

    def __repr__(self):
        return f"<PaperList(id={self.id}, title={self.title}, abstract={self.abstract}, pdf={self.pdf_url}, first_author={self.first_author}, category_id={self.category_id}, submitted_time={self.submitted_at})>"