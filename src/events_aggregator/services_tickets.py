from uuid import UUID

from events_aggregator.clients.events_provider import EventsProviderClient
from events_aggregator.repositories import TicketRepository
from events_aggregator.schemas.tickets import TicketCreateRequest


class TicketService:
    def __init__(
        self,
        repository: TicketRepository,
        client: EventsProviderClient,
    ):
        self.repository = repository
        self.client = client

    async def register_ticket(
        self,
        ticket_data: TicketCreateRequest,
    ):
        try:
            event_id = UUID(ticket_data.event_id)
        except ValueError as exc:
            raise ValueError("Invalid event_id") from exc

        if "@" not in ticket_data.email:
            raise ValueError("Invalid email")

        try:
            ticket_id = await self.client.register(
                event_id=str(event_id),
                first_name=ticket_data.first_name,
                last_name=ticket_data.last_name,
                email=ticket_data.email,
                seat=ticket_data.seat,
            )
        except Exception as exc:
            raise RuntimeError(f"Failed to register ticket: {exc}") from exc

        return await self.repository.create(
            event_id=event_id,
            ticket_id=UUID(ticket_id),
            first_name=ticket_data.first_name,
            last_name=ticket_data.last_name,
            email=ticket_data.email,
            seat=ticket_data.seat,
        )
