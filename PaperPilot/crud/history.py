from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from models.history import PaperBrowserHistory
from datetime import datetime
from models.papers import PapersList, Categories


async def add_papers_history(db: AsyncSession, user_id: int, paperId: int):
    result = await db.execute(
        select(PaperBrowserHistory).where(
            PaperBrowserHistory.user_id == user_id,
            PaperBrowserHistory.paper_id == paperId
        )
    )
    existing = result.scalar_one_or_none()

    if existing is not None:
        existing.view_time = datetime.now()
        await db.commit()
        await db.refresh(existing)
        history = existing
    else:
        history_paper = PaperBrowserHistory(user_id=user_id, paper_id=paperId)
        db.add(history_paper)
        await db.commit()
        await db.refresh(history_paper)
        history = history_paper

    paper_result = await db.execute(
        select(PapersList.paper_id).where(PapersList.id == paperId)
    )
    paper_string_id = paper_result.scalar_one_or_none()

    return {
        "historyId": history.id,
        "userId": history.user_id,
        "paperId": paper_string_id,
        "viewTime": history.view_time
    }

async def get_history_list(db: AsyncSession, user_id: int, page: int = 1, pageSize: int = 10):
    skip = (page - 1) * pageSize
    stmt = (
        select(PaperBrowserHistory)
        .where(PaperBrowserHistory.user_id == user_id)
        .order_by(PaperBrowserHistory.view_time.desc())
        .offset(skip)
        .limit(pageSize)
    )
    result = await db.execute(stmt)
    total_result = await db.execute(
        select(func.count(PaperBrowserHistory.id)).where(PaperBrowserHistory.user_id == user_id)
    )
    history_list = result.scalars().all()

    data = []
    for h in history_list:
        paper_result = await db.execute(
            select(PapersList).where(PapersList.id == h.paper_id)
        )
        paper = paper_result.scalar_one_or_none()
        if not paper:
            continue

        cat_result = await db.execute(
            select(Categories.name).where(Categories.id == paper.category_id)
        )
        category_name = cat_result.scalar_one_or_none()

        data.append({
            "historyId": h.id,
            "viewTime": h.view_time.strftime("%Y-%m-%dT%H:%M:%S") if h.view_time else None,
            "paper": {
                "id": paper.id,
                "paper_id": paper.paper_id,
                "title": paper.title,
                "abstract": paper.abstract,
                "first_author": paper.first_author,
                "submitted_at": paper.submitted_at.strftime("%Y-%m-%d") if paper.submitted_at else None,
                "category_name": category_name,
                "pdf_url": paper.pdf_url,
                "arxiv_url": paper.arxiv_url,
            }
        })
    return data, total_result.scalar_one()

async def delete_papers_history(db: AsyncSession, user_id: int, historyId: int):
    query = delete(PaperBrowserHistory).where(PaperBrowserHistory.user_id==user_id, PaperBrowserHistory.id==historyId)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0

async def get_clear_history(db: AsyncSession, user_id: int):
    query = delete(PaperBrowserHistory).where(PaperBrowserHistory.user_id==user_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0