from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AIA SupportOps Automation"
    app_version: str = "0.4.0"
    database_url: str = "sqlite:///./supportops.db"

    ai_provider: str = "openai-compatible"
    ai_base_url: str = "https://api.groq.com/openai/v1"
    ai_model: str = "llama-3.1-8b-instant"
    ai_api_key: str | None = None
    ai_timeout_seconds: float = 15.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
