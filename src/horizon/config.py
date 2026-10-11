from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables and `.env`."""

    app_env: str = Field(default="development")
    database_url: str = Field(default="sqlite:///./horizon.db")
    project_code: str = Field(default="DH-05")
    data_root: Path = Field(default=Path("./data"))
    mocks_root: Path = Field(default=Path("./mocks"))
    rules_root: Path = Field(default=Path("./config/rules"))
    log_level: str = Field(default="INFO")
    mock_identity_enabled: bool = Field(default=True)
    # Simulates a failure of the Employer Directory mock (for example EMP-503).
    mock_employer_failure: str | None = Field(default=None)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
