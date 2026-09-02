from collections.abc import AsyncIterator

from events_aggregator.clients.events_provider import EventsProviderClient


class EventsPaginator:
    def __init__(self, client: EventsProviderClient, changed_at: str | None):
        self.client = client
        self.changed_at = changed_at

    async def __aiter__(self) -> AsyncIterator[dict]:
        page = await self.client.events(self.changed_at)

        while True:
            for event in page.get("results", []):
                yield event

            next_url = page.get("next")

            if not next_url:
                break

            page = await self.client.events_page(next_url)
