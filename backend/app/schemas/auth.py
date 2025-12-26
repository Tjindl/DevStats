from app.schemas.user import UserOut
from pydantic import BaseModel


class LoginResponse(BaseModel):
    authorization_url: str
    state: str


class AuthCallbackRequest(BaseModel):
    code: str
    state: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
