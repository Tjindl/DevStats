import uuid
from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    id: uuid.UUID
    github_id: int
    username: str
    avatar_url: str | None = None

    model_config = ConfigDict(from_attributes=True)
