from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException

from events_aggregator.clients.events_provider import EventsProviderClient
from events_aggregator.core.config import settings
from events_aggregator.schemas.seats import SeatsResponse

router = APIRouter(
    prefix="/api/events",
    tags=["seats"],
)


def get_events_provider_client() -> EventsProviderClient:
    return EventsProviderClient(
        base_url=settings.events_provider_url,
        api_key=settings.events_provider_api_key,
    )


@router.get("/{event_id}/seats", response_model=SeatsResponse)
async def get_event_seats(
    event_id: UUID,
    client: EventsProviderClient = Depends(
        get_events_provider_client,
    ),
) -> SeatsResponse:
    try:
        seats = await client.seats(str(event_id))
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="Event not found",
            ) from exc

        raise HTTPException(
            status_code=502,
            detail="Failed to get event seats",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to get event seats",
        ) from exc

    return SeatsResponse(
        event_id=event_id,
        available_seats=seats,
    )
