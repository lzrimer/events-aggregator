from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.clients.events_provider import EventsProviderClient
from events_aggregator.core.config import settings
from events_aggregator.core.database import get_session
from events_aggregator.repositories import EventRepository, SyncRepository
from events_aggregator.services import EventSyncService


router = APIRouter(
    prefix="/api/sync",
    tags=["sync"],
)


def get_events_provider_client() -> EventsProviderClient:
    return EventsProviderClient(
        base_url=settings.events_provider_url,
        api_key=settings.events_provider_api_key,
    )


@router.post("")
@router.post("/trigger")
async def sync_events(
    date_from: date | None = None,
    session: Annotated[
        AsyncSession,
        Depends(get_session),
    ] = None,
    client: Annotated[
        EventsProviderClient,
        Depends(get_events_provider_client),
    ] = None,
) -> dict[str, int]:
    repository = EventRepository(session)
    sync_repository = SyncRepository(session)

    service = EventSyncService(
        client=client,
        repository=repository,
        sync_repository=sync_repository,
    )

    count = await service.sync(date_from)

    return {"synced": count}