from datetime import UTC, date, datetime, time
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.core.database import get_session
from events_aggregator.repositories import EventRepository
from events_aggregator.schemas.events import (
    EventListResponse,
    EventResponse,
    PlaceResponse,
)

router = APIRouter(prefix="/api/events", tags=["events"])


def build_event_response(event) -> EventResponse:
    return EventResponse(
        id=event.id,
        name=event.name,
        place=PlaceResponse(
            id=event.place.id,
            name=event.place.name,
            city=event.place.city,
            address=event.place.address,
            seats_pattern=event.place.seats_pattern,
        ),
        event_time=event.event_time,
        registration_deadline=event.registration_deadline,
        status=event.status,
        number_of_visitors=event.number_of_visitors,
    )


@router.get("", response_model=EventListResponse)
async def get_events(
    date_from: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> EventListResponse:
    repository = EventRepository(session)

    date_from_datetime = None

    if date_from is not None:
        date_from_datetime = datetime.combine(
            date_from,
            time.min,
            tzinfo=UTC,
        )

    offset = (page - 1) * page_size

    events, count = await repository.get_all(
        date_from=date_from_datetime,
        offset=offset,
        limit=page_size,
    )

    results = [build_event_response(event) for event in events]

    next_page = page + 1 if offset + len(results) < count else None
    previous_page = page - 1 if page > 1 else None

    return EventListResponse(
        count=count,
        next=(
            f"/api/events?page={next_page}&page_size={page_size}" if next_page else None
        ),
        previous=(
            f"/api/events?page={previous_page}&page_size={page_size}"
            if previous_page
            else None
        ),
        results=results,
    )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> EventResponse:
    repository = EventRepository(session)

    event = await repository.get(event_id)

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found",
        )

    return build_event_response(event)
