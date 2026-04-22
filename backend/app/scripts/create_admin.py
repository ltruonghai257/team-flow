"""CLI script to create or promote a user to admin.

Usage (environment variables):
  ADMIN_EMAIL=admin@example.com \
  ADMIN_USERNAME=admin \
  ADMIN_FULL_NAME="Admin User" \
  ADMIN_PASSWORD=secret \
  python -m app.scripts.create_admin

Or run without env vars and the script will prompt interactively.
"""

import asyncio
import os
import sys


async def main() -> None:
    email = os.environ.get("ADMIN_EMAIL") or input("Email: ").strip()
    username = os.environ.get("ADMIN_USERNAME") or input("Username: ").strip()
    full_name = os.environ.get("ADMIN_FULL_NAME") or input("Full name: ").strip()
    password = os.environ.get("ADMIN_PASSWORD") or input("Password: ").strip()

    if not all([email, username, full_name, password]):
        print("ERROR: All fields (email, username, full_name, password) are required.", file=sys.stderr)
        sys.exit(1)

    from sqlalchemy import select
    from app.database import AsyncSessionLocal
    from app.models import User, UserRole
    from app.auth import hash_password

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if user:
            user.role = UserRole.admin
            await db.commit()
            print(f"Promoted existing user '{user.username}' to admin.")
        else:
            user = User(
                email=email,
                username=username,
                full_name=full_name,
                hashed_password=hash_password(password),
                role=UserRole.admin,
                is_active=True,
            )
            db.add(user)
            await db.commit()
            print(f"Created admin user '{username}' ({email}).")


if __name__ == "__main__":
    asyncio.run(main())
