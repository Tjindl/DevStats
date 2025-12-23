from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import encrypt_token
from app.models.user import User


async def get_by_github_id(db: AsyncSession, github_id: int) -> User | None:
    result = await db.execute(select(User).where(User.github_id == github_id))
    return result.scalar_one_or_none()


async def create_or_update_from_github(
    db: AsyncSession,
    github_user: dict[str, Any],
    access_token: str,
) -> User:
    """
    Upsert a user from GitHub user payload and store encrypted token.
    """
    github_id = github_user["id"]
    user = await get_by_github_id(db, github_id=github_id)
    encrypted = encrypt_token(access_token)

    if user:
        user.username = github_user.get("login", user.username)
        user.avatar_url = github_user.get("avatar_url", user.avatar_url)
        user.access_token_encrypted = encrypted
        user.created_at = user.created_at or datetime.now(timezone.utc)
    else:
        user = User(
            github_id=github_id,
            username=github_user.get("login") or "",
            avatar_url=github_user.get("avatar_url"),
            access_token_encrypted=encrypted,
            created_at=datetime.now(timezone.utc),
        )
        db.add(user)

    await db.commit()
    await db.refresh(user)
    return user
