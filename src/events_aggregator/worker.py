import asyncio
import logging

from events_aggregator.clients.events_provider import EventsProviderClient
from events_aggregator.core.config import settings
from events_aggregator.core.database import async_session_factory
from events_aggregator.repositories import EventRepository, SyncRepository
from events_aggregator.services import EventSyncService

logger = logging.getLogger(__name__)

SYNC_INTERVAL = 24 * 60 * 60
RETRY_INTERVAL = 60


async def sync_worker() -> None:
    while True:
        try:
            async with async_session_factory() as session:
                service = EventSyncService(
                    client=EventsProviderClient(
                        base_url=settings.events_provider_url,
                        api_key=settings.events_provider_api_key,
                    ),
                    repository=EventRepository(session),
                    sync_repository=SyncRepository(session),
                )

                await service.sync()

        except Exception:
            logger.exception("Event synchronization failed")
            await asyncio.sleep(RETRY_INTERVAL)
            continue

        await asyncio.sleep(SYNC_INTERVAL)
