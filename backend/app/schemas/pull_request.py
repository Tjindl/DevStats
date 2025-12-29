from datetime import datetime

from pydantic import BaseModel, Field


class PullRequestInfo(BaseModel):
    """
    Core PR metadata (identity + display).
    """

    repo: str = Field(
        ...,
        description="Base repository full name (owner/repo)"
    )
    pr_number: int = Field(
        ...,
        ge=1,
        description="Pull request number"
    )
    title: str = Field(
        ...,
        description="PR title"
    )
    body: str | None = Field(
        None,
        description="PR description/body"
    )
    state: str = Field(
        ...,
        description="PR state: open / closed / merged"
    )
    created_at: datetime = Field(
        ...,
        description="PR creation timestamp"
    )
    merged: bool = Field(
        ...,
        description="Whether the PR was merged"
    )


class PRParameters(BaseModel):
    """
    Quantitative parameters used for PR scoring and analytics.
    """

    lines_added: int = Field(
        ...,
        ge=0,
        description="Lines of code added"
    )
    lines_removed: int = Field(
        ...,
        ge=0,
        description="Lines of code removed"
    )
    files_changed: int = Field(
        ...,
        ge=0,
        description="Number of files changed"
    )
    commits: int = Field(
        ...,
        ge=0,
        description="Number of commits in the PR"
    )

    pr_opened: datetime = Field(
        ...,
        description="PR opened timestamp"
    )
    pr_closed: datetime | None = Field(
        None,
        description="PR closed or merged timestamp (None if still open)"
    )

    repo_stars: int = Field(
        ...,
        ge=0,
        description="Star count of the base repository"
    )
    repo_forks: int = Field(
        ...,
        ge=0,
        description="Fork count of the base repository"
    )
