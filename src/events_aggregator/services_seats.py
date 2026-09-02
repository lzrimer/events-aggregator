import time
from uuid import UUID

import httpx

from events_aggregator.clients.events_provider import EventsProviderClient


class SeatsService:
    CACHE_TTL = 30.0

    def __init__(self, client: EventsProviderClient):
        self.client = client
        self._cache: dict[UUID, tuple[float, list[str]]] = {}

    async def get_seats(self, event_id: UUID) -> list[str]:
        now = time.monotonic()
        cached = self._cache.get(event_id)

        if cached is not None:
            cached_at, seats = cached
            if now - cached_at < self.CACHE_TTL:
                return seats

        try:
            seats = await self.client.seats(str(event_id))
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise ValueError("Event not found") from exc

            raise RuntimeError("Failed to get event seats") from exc
        except httpx.HTTPError as exc:
            raise RuntimeError("Failed to get event seats") from exc

        self._cache[event_id] = (now, seats)

        return seats
