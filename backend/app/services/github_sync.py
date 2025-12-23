from datetime import datetime
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decrypt_token
from app.integrations.github_client import GithubClient
from app.models.pull_request import PullRequest
from app.models.user import User
from app.services.scoring_service import apply_score


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        # GitHub returns ISO 8601 with Z
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


async def sync_pull_requests(
    db: AsyncSession,
    user: User,
    days: int = 30,
    limit: int = 20,
) -> list[PullRequest]:
    """
    Fetch recent pull requests from GitHub and upsert them locally.
    """
    if not user.access_token_encrypted:
        return []

    token = decrypt_token(user.access_token_encrypted)
    gh = GithubClient(token)
    prs_data = await gh.fetch_recent_pull_requests(
        username=user.username,
        days=days,
        limit=limit,
    )

    stored: list[PullRequest] = []
    for pr_data in prs_data:
        github_pr_id = pr_data.get("id")
        if github_pr_id is None:
            continue

        repo_full_name = pr_data.get("base", {}).get("repo", {}).get("full_name") or ""
        repo_owner = pr_data.get("base", {}).get("repo", {}).get("owner", {}).get("login") or ""
        merged_at = _parse_dt(pr_data.get("merged_at"))
        additions = pr_data.get("additions") or 0
        deletions = pr_data.get("deletions") or 0
        changed_files = pr_data.get("changed_files") or 0
        review_count = pr_data.get("review_comments") or 0
        ci_passed = pr_data.get("mergeable_state") in {"clean", "stable"}

        result = await db.execute(
            select(PullRequest).where(PullRequest.github_pr_id == github_pr_id)
        )
        pr = result.scalar_one_or_none()
        if pr:
            pr.repo_full_name = repo_full_name
            pr.repo_owner = repo_owner
            pr.merged_at = merged_at
            pr.additions = additions
            pr.deletions = deletions
            pr.changed_files = changed_files
            pr.review_count = review_count
            pr.ci_passed = ci_passed
        else:
            pr = PullRequest(
                github_pr_id=github_pr_id,
                repo_full_name=repo_full_name,
                repo_owner=repo_owner,
                merged_at=merged_at,
                additions=additions,
                deletions=deletions,
                changed_files=changed_files,
                review_count=review_count,
                ci_passed=ci_passed,
                user_id=user.id,
            )
            db.add(pr)

        apply_score(pr)
        stored.append(pr)

    await db.commit()
    for pr in stored:
        await db.refresh(pr)
    return stored
