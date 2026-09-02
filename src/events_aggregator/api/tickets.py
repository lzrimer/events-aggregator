from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.clients.events_provider import EventsProviderClient
from events_aggregator.core.config import settings
from events_aggregator.core.database import get_session
from events_aggregator.repositories import TicketRepository
from events_aggregator.schemas.tickets import (
    TicketCreateRequest,
    TicketResponse,
)

router = APIRouter(
    prefix="/api/tickets",
    tags=["tickets"],
)


def get_events_provider_client() -> EventsProviderClient:
    return EventsProviderClient(
        base_url=settings.events_provider_url,
        api_key=settings.events_provider_api_key,
    )


@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_ticket(
    ticket_data: TicketCreateRequest,
    session: AsyncSession = Depends(get_session),
    client: EventsProviderClient = Depends(
        get_events_provider_client,
    ),
) -> TicketResponse:
    repository = TicketRepository(session)

    try:
        event_id = UUID(ticket_data.event_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid event_id",
        ) from exc

    if "@" not in ticket_data.email:
        raise HTTPException(
            status_code=400,
            detail="Invalid email",
        )

    try:
        ticket_id = await client.register(
            event_id=str(event_id),
            first_name=ticket_data.first_name,
            last_name=ticket_data.last_name,
            email=ticket_data.email,
            seat=ticket_data.seat,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to register ticket: {exc}",
        ) from exc

    ticket = await repository.create(
        event_id=event_id,
        ticket_id=UUID(ticket_id),
        first_name=ticket_data.first_name,
        last_name=ticket_data.last_name,
        email=ticket_data.email,
        seat=ticket_data.seat,
    )

    return TicketResponse(
        ticket_id=ticket.ticket_id,
        event_id=ticket.event_id,
        first_name=ticket.first_name,
        last_name=ticket.last_name,
        email=ticket.email,
        seat=ticket.seat,
    )


@router.delete(
    "/{ticket_id}",
)
async def unregister_ticket(
    ticket_id: UUID,
    session: AsyncSession = Depends(get_session),
    client: EventsProviderClient = Depends(
        get_events_provider_client,
    ),
) -> dict[str, bool]:
    repository = TicketRepository(session)

    ticket = await repository.get(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    try:
        success = await client.unregister(
            event_id=str(ticket.event_id),
            ticket_id=str(ticket.ticket_id),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to unregister ticket",
        ) from exc

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Ticket was not unregistered",
        )

    await repository.delete(ticket)

    return {"success": True}
