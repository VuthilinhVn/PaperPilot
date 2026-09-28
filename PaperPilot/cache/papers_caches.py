"""
新闻相关的缓存方法
key - value => 设计新闻key
"""
from config.cache_conf import get_json_cache, set_caches
from typing import List, Dict, Any, Optional

from models.papers import PapersList

CATEGORIES_KEY = "news:categories"
PAPERLIST_PREFIX = "news:papers_list"
# 获取新闻分类
async def get_cached_categories():
    return await get_json_cache(CATEGORIES_KEY)
# 写入新闻分类缓存
"""
过期时间在开发过程常用:
- 分类: 7200
- 列表: 3600
- 详情: 1800
-验证码: 120
==> 数据为稳定, 时间越长越好
"""
async def set_cached_categories(data: List[Dict[str,Any]], expire:int=7200): # key, value, ex
    return await set_caches(CATEGORIES_KEY, data, expire)

async def get_cached_papers_list(category_id: Optional[int], page: int, pageSize: int):
    category_part = category_id if category_id is not None else "all"
    key = f"{PAPERLIST_PREFIX}{category_part}:{page}:{pageSize}"
    return await get_json_cache(key)

# 写入缓存-新闻列表key = papers_list: 分类Id: 页码: 每页数量 + 列表数据, 过期时间
async def set_cached_papers_list(category_id: Optional[int], page: int, pageSize: int, papers_list: List[Dict[str, Any]], ex: int = 1800): # key, value, ex
    category_part =  category_id if category_id is not None else "all"
    key = f"{PAPERLIST_PREFIX}{category_part}:{page}:{pageSize}"
    return await set_caches(key, papers_list, ex)
