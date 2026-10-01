from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AIA SupportOps Automation"
    app_version: str = "0.10.0"
    environment: str = "development"
    database_url: str = "sqlite:///./supportops.db"

    demo_safe_mode: bool = False
    demo_allow_external_ai: bool = False
    demo_allow_external_automation: bool = False

    ai_provider: str = "openai-compatible"
    ai_base_url: str = "https://api.groq.com/openai/v1"
    ai_model: str = "llama-3.1-8b-instant"
    ai_api_key: str | None = None
    ai_timeout_seconds: float = 15.0

    n8n_webhook_url: str | None = None
    n8n_webhook_secret: str | None = None
    automation_timeout_seconds: float = 5.0
    automation_max_attempts: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
