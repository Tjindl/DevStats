import uuid
from datetime import datetime

from app.db.base import Base
from sqlalchemy import (BigInteger, Boolean, DateTime, ForeignKey, Integer,
                        String)
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PullRequest(Base):
    __tablename__ = "pull_requests"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    github_pr_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
    )

    repo_full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    repo_owner: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    merged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    additions: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    deletions: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    changed_files: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    review_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    ci_passed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships
    user = relationship(
        "User",
        back_populates="pull_requests",
    )
