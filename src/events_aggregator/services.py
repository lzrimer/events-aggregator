from datetime import UTC, date, datetime

from events_aggregator.clients.events_provider import EventsProviderClient
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

        events_data = await self.client.events(
            date_from.isoformat() if date_from else None
        )

        count = 0
        last_changed_at = None

        while True:
            results = events_data.get("results", [])

            for event_data in results:
                await self.repository.save(event_data)
                count += 1

                changed_at = event_data.get("changed_at")

                if changed_at and (
                    last_changed_at is None or changed_at > last_changed_at
                ):
                    last_changed_at = changed_at

            next_url = events_data.get("next")

            if not next_url:
                break

            events_data = await self.client.events_page(next_url)

        last_changed_at_datetime = None

        if last_changed_at:
            last_changed_at_datetime = datetime.fromisoformat(last_changed_at)

        await self.sync_repository.save(
            last_sync_time=started_at,
            last_changed_at=last_changed_at_datetime,
            sync_status="success",
        )

        return count
