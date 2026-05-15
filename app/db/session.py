from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# Create asynchronous engine
db_url = settings.get_database_url()
connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}

engine = create_async_engine(
    db_url,
    echo=True,  # Set to False in production
    future=True,
    connect_args=connect_args
)

# Create asynchronous session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Dependency to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
