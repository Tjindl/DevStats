from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PullRequestOut(BaseModel):
    id: int
    github_pr_id: int
    repo_full_name: str
    repo_owner: str
    merged_at: datetime | None = None
    additions: int
    deletions: int
    changed_files: int
    review_count: int
    ci_passed: bool
    score: int

    model_config = ConfigDict(from_attributes=True)
