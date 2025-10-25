from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import settings

engine = create_async_engine(settings.database_url, echo=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with SessionLocal() as session:
        yield session


async def connect_to_pg():
    async with engine.begin() as conn:
        await conn.run_sync(lambda _: None)


async def close_pg():
    await engine.dispose()
