import asyncio
from sqlalchemy import update
from app.db.session import AsyncSessionLocal
from app.models.user import User

async def repair_db():
    async with AsyncSessionLocal() as db:
        # Ensure no NULLs in boolean fields
        await db.execute(update(User).where(User.is_active == None).values(is_active=True))
        await db.execute(update(User).where(User.is_superuser == None).values(is_superuser=False))
        await db.commit()
        print("Database fields repaired successfully.")

if __name__ == "__main__":
    asyncio.run(repair_db())
