from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://interviewelo:interviewelo@localhost:5432/interviewelo"
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    cors_origins: list[str] = ["http://localhost:5173"]
    cookie_secure: bool = False
    cookie_samesite: str = "lax"
    anthropic_api_key: str | None = None
    grading_model: str = "claude-sonnet-5"
    runner_shared_secret: str | None = None
    runner_url: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
