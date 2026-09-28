from typing import Any

import redis.asyncio as redis
import json

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
# 创建Redis对象
redis_client = redis.Redis(
    host=REDIS_HOST, # Redis服务器地址
    port=REDIS_PORT, # Redis服务器端口
    db = REDIS_DB, # Redis数据库编号, 0~15
    decode_responses=True, # 是否将字节数据自动解码为字符串
    protocol=2
)

# 设置 和读取 (字符串 和 列表或字典) "[{}]"
# 读取: 字符串
async def get_cache(key: str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败: {e}")
        return None
# 读取: 列表 或字典
async def get_json_cache(key: str):
    try:
        data =  await redis_client.get(key)
        if data:
            return json.loads(data) # 序列化为Python对象
    except Exception as e:
        print(f"获取json缓存失败: {e}")
        return None
# 设置缓存key: str, ex
async def set_caches(key: str, value: Any, ex: int=3600):
    try:
        if isinstance(value, (dict, list)):
            #转字符串在存
            value = json.dumps(value, ensure_ascii=False)  # 保留中文
        await redis_client.setex(key, ex, value)
        return True
    except Exception as e:
        print(f"设置缓存失败: {e}")
        return False
