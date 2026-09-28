from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from models.papers import Categories, PapersList
from sqlalchemy import select, func, update
from cache.papers_caches import get_cached_categories, set_cached_categories, get_cached_papers_list, set_cached_papers_list


async def get_categories(db: AsyncSession, skip: int =0 , limit: int =100):
    # 先尝试从缓存中获取数据
    cached_categories = await get_cached_categories()
    if cached_categories is not None:
        return cached_categories

    result = await db.execute(select(Categories).offset(skip).limit(limit))
    categories = result.scalars().all() # orm 结果
    # 写入缓存
    if categories:
        categories = jsonable_encoder(categories) # 转换为可序列化格式
        await set_cached_categories(categories)
    # 返回数据
    return categories


async def get_papers_list(db: AsyncSession, page: int = 0, pageSize: int = 10, categoriesId: int = 0):
    # 先查缓存
    cached_papers_list = await get_cached_papers_list(categoriesId, page, pageSize)
    if cached_papers_list is not None:
        return cached_papers_list["list"], cached_papers_list["total"]
    # 查询数据库
    skip = (page - 1) * pageSize
    stmt = select(PapersList).where(PapersList.category_id == categoriesId).offset(skip).limit(pageSize)
    result = await db.execute(stmt)
    total = await db.execute(select(func.count(PapersList.id)).where(PapersList.category_id == categoriesId))
    papers_list = result.scalars().all()
    total_count = total.scalar_one()

    # 写入缓存
    if papers_list:
        papers_data = {
            "list": jsonable_encoder(papers_list),
            "total": total_count
        }
        await set_cached_papers_list(categoriesId, page, pageSize, papers_data)

    return papers_list, total_count

async def get_details(db: AsyncSession, id: int):
    stmt = select(PapersList).where(PapersList.id == id)
    result = await db.execute(stmt)
    data = result.scalar_one_or_none()
    if not data:
        return None, []
    related = await db.execute(select(PapersList).where(
        PapersList.id != data.id,
        PapersList.category_id == data.category_id
    ).order_by(PapersList.submitted_at.desc()).limit(3))
    related_news = related.scalars().all()
    return data, [{"id": r.id,
            "title": r.title,
            "abstract": r.abstract,
            "pdf": r.pdf_url or None,
            "firstAuthor": r.first_author or None,
            "submittedAt": r.submitted_at or None,
            "categoryId": r.category_id,
            "pdfUrl": r.pdf_url or None,
            "firstAuthor": r.first_author or None,
            "submittedAt": r.submitted_at or None} for r in related_news]