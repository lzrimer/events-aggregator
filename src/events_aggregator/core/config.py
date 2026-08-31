from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(
        default=(
            "postgresql+asyncpg://postgres:postgres@"
            "localhost:5432/events_aggregator"
        ),
        validation_alias=AliasChoices(
            "POSTGRES_CONNECTION_STRING",
            "DATABASE_URL",
        ),
    )

    events_provider_url: str = (
        "https://events-provider.dev-2.python-labs.ru"
    )

    events_provider_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("database_url")
    @classmethod
    def fix_database_url(cls, value: str) -> str:
        if value.startswith("postgres://"):
            return value.replace(
                "postgres://",
                "postgresql+asyncpg://",
                1,
            )

        if value.startswith("postgresql://"):
            return value.replace(
                "postgresql://",
                "postgresql+asyncpg://",
                1,
            )

        return value


settings = Settings()