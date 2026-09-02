from datetime import UTC, date, datetime

from events_aggregator.clients.events_provider import EventsProviderClient
from events_aggregator.clients.paginator import EventsPaginator
from events_aggregator.repositories import EventRepository, SyncRepository


class EventSyncService:
    def __init__(
        self,
        client: EventsProviderClient,
        repository: EventRepository,
        sync_repository: SyncRepository,
    ):
        self.client = client
        self.repository = repository
        self.sync_repository = sync_repository

    async def sync(self, date_from: date | None = None) -> int:
        started_at = datetime.now(UTC)

        last_sync = await self.sync_repository.get()

        if date_from is not None:
            changed_at = date_from.isoformat()
        elif last_sync is not None and last_sync.last_changed_at is not None:
            changed_at = last_sync.last_changed_at.isoformat()
        else:
            changed_at = None

        count = 0
        last_changed_at = None

        paginator = EventsPaginator(self.client, changed_at)

        async for event_data in paginator:
            await self.repository.save(event_data)
            count += 1

            event_changed_at = event_data.get("changed_at")

            if event_changed_at and (
                last_changed_at is None or event_changed_at > last_changed_at
            ):
                last_changed_at = event_changed_at

        last_changed_at_datetime = None

        if last_changed_at:
            last_changed_at_datetime = datetime.fromisoformat(last_changed_at)

        await self.sync_repository.save(
            last_sync_time=started_at,
            last_changed_at=last_changed_at_datetime,
            sync_status="success",
        )

        return count
