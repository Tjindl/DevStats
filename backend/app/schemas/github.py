from datetime import datetime

from pydantic import BaseModel


class PullRequestInfo(BaseModel):
    repo: str
    pr_number: int
    title: str | None = None
    body: str | None = None
    state: str | None = None
    created_at: datetime | None = None
    merged: bool = False
