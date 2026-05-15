import asyncio
import sys
import os

# Add the project root to sys.path to allow importing from 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import engine
from app.models.user import Base

async def init_db():
    print("Connecting to database...")
    async with engine.begin() as conn:
        print("Creating tables...")
        # This will create all tables defined with Base
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized successfully!")
    await engine.dispose()

if __name__ == "__main__":
    try:
        asyncio.run(init_db())
    except Exception as e:
        print(f"Error initializing database: {e}")
        print("\nMake sure your PostgreSQL server is running and the database 'auth_db' exists.")
