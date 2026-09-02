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
from events_aggregator.services_tickets import TicketService

router = APIRouter(
    prefix="/api/tickets",
    tags=["tickets"],
)


def get_events_provider_client() -> EventsProviderClient:
    return EventsProviderClient(
        base_url=settings.events_provider_url,
        api_key=settings.events_provider_api_key,
    )


def get_ticket_service(
    session: AsyncSession = Depends(get_session),
    client: EventsProviderClient = Depends(get_events_provider_client),
) -> TicketService:
    return TicketService(
        repository=TicketRepository(session),
        client=client,
    )


@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_ticket(
    ticket_data: TicketCreateRequest,
    service: TicketService = Depends(get_ticket_service),
) -> TicketResponse:
    try:
        ticket = await service.register_ticket(ticket_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

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
    service: TicketService = Depends(get_ticket_service),
) -> dict[str, bool]:
    try:
        await service.unregister_ticket(ticket_id)
    except ValueError as exc:
        if str(exc) == "Ticket not found":
            raise HTTPException(
                status_code=404,
                detail=str(exc),
            ) from exc

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    return {"success": True}
