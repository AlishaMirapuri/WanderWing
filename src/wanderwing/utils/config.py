"""Application configuration management."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = Field(default="sqlite:///./data/wanderwing.db")

    # LLM Provider
    llm_provider: Literal["openai", "anthropic"] = Field(default="openai")
    openai_api_key: str | None = Field(default=None)
    anthropic_api_key: str | None = Field(default=None)
    llm_model: str = Field(default="gpt-4-turbo-preview")
    llm_temperature: float = Field(default=0.1)
    llm_max_tokens: int = Field(default=2000)
    llm_timeout_seconds: int = Field(default=30)

    # API
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_reload: bool = Field(default=True)

    # Frontend
    frontend_port: int = Field(default=8501)

    # Application
    enable_experiments: bool = Field(default=True)
    experiment_config_path: str = Field(default="./data/experiments.json")
    log_level: str = Field(default="INFO")
    log_format: Literal["json", "text"] = Field(default="json")

    # Security
    secret_key: str = Field(default="dev-secret-key-change-in-production")
    cors_origins: list[str] = Field(default=["http://localhost:8501"])

    # Feature Flags
    enable_caching: bool = Field(default=True)
    enable_rate_limiting: bool = Field(default=False)
    rate_limit_per_minute: int = Field(default=60)

    # Cost Control
    max_llm_calls_per_user_per_hour: int = Field(default=50)
    alert_cost_threshold_usd: float = Field(default=10.0)

    # Matching Configuration
    max_matches_per_trip: int = Field(default=10)
    matching_frequency_hours: int = Field(default=1)
    llm_similarity_weight: float = Field(default=0.6)
    rule_based_weight: float = Field(default=0.4)

    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return self.database_url.startswith("sqlite")

    @property
    def is_postgres(self) -> bool:
        """Check if using PostgreSQL database."""
        return self.database_url.startswith("postgresql")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
