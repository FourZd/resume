from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from configs.environment import get_environment_variables
settings = get_environment_variables()
DATABASE_URL = (
    f"{settings.DATABASE_DIALECT}+asyncpg://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}"
    f"@{settings.DATABASE_HOSTNAME}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
)
metadata = MetaData()

Base = declarative_base(metadata=metadata)


Engine = create_async_engine(
    DATABASE_URL, future=True
)

AsyncSessionLocal = sessionmaker(
    bind=Engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
