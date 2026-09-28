from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/papers_app?charset=utf8mb4"
async_engine = create_async_engine(DATABASE_URL, echo=True, pool_size=10, max_overflow=20)

# khoi tao bang ==> da tu sql ra roi

#创建异步引擎
AsyncSessionLocal = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

#创建异步会话
async def get_database():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

