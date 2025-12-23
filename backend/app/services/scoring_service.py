from datetime import datetime

from app.models.pull_request import PullRequest


def _base_score(merged: bool) -> int:
    return 15 if merged else 5


def compute_score_from_metrics(
    merged_at: datetime | None,
    additions: int,
    deletions: int,
    changed_files: int,
    review_count: int,
    ci_passed: bool,
) -> int:
    merged = merged_at is not None
    score = _base_score(merged)
    score += min(additions // 50, 20)
    score += min(deletions // 50, 10)
    score += min(changed_files * 2, 10)
    score += review_count * 5
    if ci_passed:
        score += 10
    return max(score, 0)


def apply_score(pr: PullRequest) -> None:
    """Mutate a PullRequest with a derived score."""
    pr.score = compute_score_from_metrics(
        merged_at=pr.merged_at,
        additions=pr.additions,
        deletions=pr.deletions,
        changed_files=pr.changed_files,
        review_count=pr.review_count,
        ci_passed=pr.ci_passed,
    )
