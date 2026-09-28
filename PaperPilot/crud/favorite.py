from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from models.favourite import Favorite
from models.papers import PapersList

from crud.papers import get_details
# 检查当前用户是否收藏了这条论文
async def is_papers_favorite(db: AsyncSession, user_id: int, paperId: int):
    query = select(Favorite).where(Favorite.user_id == user_id, Favorite.paper_id == paperId)
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None # return 结果是True or False

# 添加收藏 -> 添加数据
async def add_papers_favorite(db: AsyncSession, user_id: int, paperId: int):
    favorite = (Favorite(user_id=user_id, paper_id=paperId))
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

async def delete_papers_favorite(db: AsyncSession, user_id: int, paperId: int):
    query = delete(Favorite).where(Favorite.user_id==user_id, Favorite.paper_id==paperId)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0

async def get_favorite_list(db: AsyncSession, user_id: int, page: int = 0, pageSize: int = 10):
    skip = (page - 1) * pageSize
    stmt = select(Favorite).where(Favorite.user_id == user_id).offset(skip).limit(pageSize)
    result = await db.execute(stmt)
    total = await db.execute(select(func.count(Favorite.id)).where(Favorite.user_id == user_id))
    favorited_list = result.scalars().all()
    data = []
    for fav in favorited_list:
        paper_result = await db.execute(select(PapersList).where(PapersList.id == fav.paper_id))
        paper = paper_result.scalar_one_or_none()
        if paper:
            data.append({
                "id": paper.id,
                "title": paper.title,
                "abstract": paper.abstract,
                "author": paper.first_author,
                "paperId": paper.paper_id,
                "favoriteTime": fav.created_at
            })
    return data, total.scalar_one() # 只返回一个值, 否则报错

async def clear_paper_favorite(db: AsyncSession, user_id: int):
    query = delete(Favorite).where(Favorite.user_id==user_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0