import asyncio
from sqlalchemy import text
from app.db.database import engine

async def fix_alembic_version():
    async with engine.begin() as conn:
        await conn.execute(text("UPDATE alembic_version SET version_num = '76d2b3f4f184'"))
        print("Updated alembic_version to 76d2b3f4f184.")

if __name__ == "__main__":
    asyncio.run(fix_alembic_version())
