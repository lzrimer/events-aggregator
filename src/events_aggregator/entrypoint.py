import asyncio
import os
import subprocess
import sys

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine

from events_aggregator.core.config import settings

REQUIRED_TABLES = {
    "places",
    "events",
    "tickets",
    "sync_metadata",
}


async def get_database_tables() -> set[str]:
    engine = create_async_engine(settings.database_url)

    try:
        async with engine.connect() as connection:
            return await connection.run_sync(
                lambda sync_connection: set(inspect(sync_connection).get_table_names())
            )
    finally:
        await engine.dispose()


def run_command(*args: str) -> None:
    subprocess.run(args, check=True)


async def main() -> None:
    tables = await get_database_tables()

    has_alembic_version = "alembic_version" in tables
    has_application_schema = REQUIRED_TABLES.issubset(tables)
    has_partial_schema = bool(REQUIRED_TABLES.intersection(tables)) and not (
        has_application_schema
    )

    if has_partial_schema and not has_alembic_version:
        print(
            "Database contains a partial application schema without "
            "Alembic version information.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not has_alembic_version and has_application_schema:
        print(
            "Existing application schema detected. "
            "Marking current schema as Alembic head."
        )
        run_command("alembic", "stamp", "head")
    else:
        print("Applying database migrations.")
        run_command("alembic", "upgrade", "head")

    os.execvp(
        "uvicorn",
        [
            "uvicorn",
            "events_aggregator.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
        ],
    )


if __name__ == "__main__":
    asyncio.run(main())
