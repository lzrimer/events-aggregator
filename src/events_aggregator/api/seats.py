from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from events_aggregator.clients.events_provider import EventsProviderClient
from events_aggregator.core.config import settings
from events_aggregator.schemas.seats import SeatsResponse
from events_aggregator.services_seats import SeatsService

router = APIRouter(
    prefix="/api/events",
    tags=["seats"],
)


seats_service = SeatsService(
    EventsProviderClient(
        base_url=settings.events_provider_url,
        api_key=settings.events_provider_api_key,
    )
)


def get_seats_service() -> SeatsService:
    return seats_service


@router.get("/{event_id}/seats", response_model=SeatsResponse)
async def get_event_seats(
    event_id: UUID,
    service: SeatsService = Depends(get_seats_service),
) -> SeatsResponse:
    try:
        seats = await service.get_seats(event_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail="Event not found",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to get event seats",
        ) from exc

    return SeatsResponse(
        event_id=event_id,
        available_seats=seats,
    )
