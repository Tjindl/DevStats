from app.schemas.pull_request import PullRequestOut
from pydantic import BaseModel, Field


class ScoreRequest(BaseModel):
    days: int = Field(default=30, ge=1, le=180)
    limit: int = Field(default=20, ge=1, le=50)


class ScoreBreakdown(BaseModel):
    total_score: int
    pull_request_count: int
    window_days: int
    pull_requests: list[PullRequestOut]
