from fastapi import APIRouter, HTTPException
from fastapi import Query, Depends
from models.users import User
from utils.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_database
from utils.response import success_response
from crud.favorite import is_papers_favorite, add_papers_favorite, delete_papers_favorite, get_favorite_list, clear_paper_favorite
from schemas.favorite import FavoriteRequests
router = APIRouter(prefix="/api/favorite", tags=["favorite"])

@router.get("/check")
async def check_favorite(paperId: int = Query(..., alias="paperId"),
                         user: User=Depends(get_current_user),
                         db: AsyncSession = Depends(get_database)
                         ):
    is_favorited = await is_papers_favorite(db, user.id, paperId)
    return success_response(message="检查收藏成功", data={"isFavorite": is_favorited})

@router.post("/add")
async def add_favorite(data: FavoriteRequests, db: AsyncSession=Depends(get_database), user: User=Depends(get_current_user)):
    result = await add_papers_favorite(db, user.id, data.paperId)
    return success_response(message="添加收藏成功", data=result)

@router.delete("/remove")
async def remove_favorite(paperID: int=Query(..., alias="paperId"), db: AsyncSession = Depends(get_database), user: User = Depends(get_current_user)):
    result = await delete_papers_favorite(db, user.id, paperID)
    if not result:
        raise HTTPException(status_code=404, detail="收藏不存在")
    return success_response(message="删除收藏成功")

@router.get("/list")
async def favorite_paper_list(page: int = 1, pageSize: int =Query(10, le = 100, alias = "pageSize"), user:User=Depends(get_current_user), db: AsyncSession=Depends(get_database)):
    data, total = await get_favorite_list(db, user.id, page, pageSize)
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
@router.delete("/clear")
async def clear_favorite(db: AsyncSession=Depends(get_database), user: User=Depends(get_current_user)):
    result = await clear_paper_favorite(db, user.id)
    if not result:
        raise HTTPException(status_code=404, detail="收藏不存在")
    return success_response(message="清空成功")