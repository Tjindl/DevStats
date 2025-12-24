import uuid

from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import get_db
from app.integrations.github_client import GithubClient
from app.schemas.auth import AuthCallbackRequest, LoginResponse, TokenResponse
from app.schemas.user import UserOut
from app.services import user_service
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/login", response_model=LoginResponse)
async def github_login() -> LoginResponse:
    if not settings.github_client_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GitHub OAuth is not configured.",
        )
    state = uuid.uuid4().hex
    authorize_url = ("https://github.com/login/oauth/authorize"
                     f"?client_id={settings.github_client_id}"
                     f"&scope=read:user repo"
                     f"&state={state}")
    return LoginResponse(authorization_url=authorize_url, state=state)


@router.post("/callback", response_model=TokenResponse)
async def github_callback(
        payload: AuthCallbackRequest,
        db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    if not payload.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing code.",
        )

    try:
        access_token = await GithubClient.exchange_code_for_token(payload.code)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth exchange failed: {exc}",
        ) from exc

    client = GithubClient(token=access_token)
    try:
        gh_user = await client.get_user()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch GitHub user: {exc}",
        ) from exc

    user = await user_service.create_or_update_from_github(
        db,
        github_user=gh_user,
        access_token=access_token,
    )

    token = create_access_token({
        "sub": str(user.id),
        "github_id": user.github_id
    })
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))
