import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.user import User

async def promote_user():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()
        if not users:
            print("No users found in database.")
            return
        
        for user in users:
            print(f"User: {user.email}, Superuser: {user.is_superuser}")
            if not user.is_superuser:
                print(f"Promoting {user.email} to superuser...")
                user.is_superuser = True
        
        await db.commit()
        print("Update complete.")

if __name__ == "__main__":
    asyncio.run(promote_user())
