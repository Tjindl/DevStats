from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.schemas.pull_request import PullRequestOut
from app.schemas.score import ScoreBreakdown, ScoreRequest
from app.services import github_sync

router = APIRouter(prefix="/score", tags=["Score"])


@router.post("/refresh", response_model=ScoreBreakdown)
async def refresh_score(
    payload: ScoreRequest,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ScoreBreakdown:
    prs = await github_sync.sync_pull_requests(
        db=db,
        user=current_user,
        days=payload.days,
        limit=payload.limit,
    )
    total_score = sum(pr.score for pr in prs)
    return ScoreBreakdown(
        total_score=total_score,
        pull_request_count=len(prs),
        window_days=payload.days,
        pull_requests=[PullRequestOut.model_validate(pr) for pr in prs],
    )
