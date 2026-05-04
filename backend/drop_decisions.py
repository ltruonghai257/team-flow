import asyncio
from sqlalchemy import text
from app.db.database import engine

async def drop_tables():
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS milestone_decisions CASCADE"))
        # Drop enum type if it exists
        await conn.execute(text("DROP TYPE IF EXISTS milestonedecisionstatus CASCADE"))
        print("Dropped milestone_decisions table and enum type.")

if __name__ == "__main__":
    asyncio.run(drop_tables())
