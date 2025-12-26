from app.api import deps
from app.models.user import User
from app.schemas.user import UserOut
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
async def read_current_user(
        current_user: User = Depends(deps.get_current_user), ) -> UserOut:
    return UserOut.model_validate(current_user)
