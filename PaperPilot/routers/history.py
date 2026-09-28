from fastapi import APIRouter, Depends, Query, Path, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from utils.response import success_response
from config.db_conf import get_database
from utils.auth import get_current_user
from models.users import User
from schemas.history import PaperHistoryRequests
from crud.history import add_papers_history, get_history_list, delete_papers_history, get_clear_history
router = APIRouter(prefix="/api/history", tags=["history"])

@router.post("/add")
async def add_history(paperId: PaperHistoryRequests, db: AsyncSession=Depends(get_database), user: User=Depends(get_current_user)):
    result = await add_papers_history(db, user.id, paperId.paperId)
    return success_response(message="添加历史记录成功", data=result)

@router.get("/list")
async def list_history(page: int = 1, pageSize: int = Query(10, le=100, alias="pageSize"), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_database)):
    data, total = await get_history_list(db, user.id, page, pageSize)
    skip = (page - 1) * pageSize
    has_more = (skip + len(data)) < total
    return success_response(message="success", data={
        "list": data,
        "total": total,
        "hasMore": has_more
    })
@router.delete("/delete/{history_id}")
async def remove_favorite(historyId: int=Path(..., alias="history_id"), db: AsyncSession = Depends(get_database), user: User = Depends(get_current_user)):
    result = await delete_papers_history(db, user.id, historyId)
    if not result:
        raise HTTPException(status_code=404, detail="历史记录不存在")
    return success_response(message="删除历史记录成功")


@router.delete("/clear")
async def clear_history(db: AsyncSession=Depends(get_database), user: User=Depends(get_current_user)):
    result = await get_clear_history(db, user.id)
    if not result:
        raise HTTPException(status_code=404, detail="历史记录不存在")
    return success_response(message="清除历史游览成功")