from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = ""

    # GitHub OAuth
    github_client_id: str | None = None
    github_client_secret: str | None = None
    jwt_secret: str | None = None

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[3] / ".env"),
        env_ignore_empty=True,
        extra="ignore",
    )


settings = Settings()
