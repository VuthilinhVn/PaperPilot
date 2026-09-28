from fastapi import APIRouter, Depends, Query, Path, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from crud import papers
from config.db_conf import get_database


router = APIRouter(prefix="/api/papers", tags=["papers"])

@router.get("/categories")
async def get_categories(skip: int=0, limit: int=100, db: AsyncSession=Depends(get_database)):
    data = await papers.get_categories(db, skip, limit)
    return {
        "code": 200,
        "msg": "success",
        "data": data
    }

@router.get("/list")
async def get_papers_list(categoryId: int = Query(..., alias = "categoryId"), page: int = 1, pageSize: int =Query(10, le = 100, alias = "pageSize"), db: AsyncSession=Depends(get_database)):
    data, total = await papers.get_papers_list(db, page, pageSize, categoryId)
    skip = (page - 1) * pageSize
    has_more = (skip + len(data)) < total
    return {"code": 200,
            "msg": "success",
            "data": {
                "list": data,
                "total": total,
                "hasMore": has_more
            }
            }

@router.get("/detail")
async def get_details(id: int = Query(..., alias="id"), db: AsyncSession = Depends(get_database)):
    data, related_news = await papers.get_details(db, id)
    if not data:
        raise HTTPException(status_code=404, detail="新闻不存在")
    return {
  "code": 200,
  "msg": "success",
  "data": {
    "id": data.id,
    "title": data.title,
    "abstract": data.abstract,
    "first_author": data.first_author,
    "submitted_at": data.submitted_at,
    "category_id": data.category_id,
    "paperId": data.paper_id,
    "pdfUrl": data.pdf_url,
    "relatedNews": related_news
  }
}

