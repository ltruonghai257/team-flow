"""Initialize database schema from SQLAlchemy models."""

import asyncio
from app.database import engine, Base
from app import models  # Import all models to register them with Base.metadata


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database schema created successfully.")


if __name__ == "__main__":
    asyncio.run(main())
