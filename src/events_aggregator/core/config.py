from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/events_aggregator",
        validation_alias=AliasChoices(
            "POSTGRES_CONNECTION_STRING",
            "DATABASE_URL",
        ),
    )

    events_provider_url: str = "https://events-provider.dev-2.python-labs.ru"

    events_provider_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()