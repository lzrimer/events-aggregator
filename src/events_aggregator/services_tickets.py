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
            ticket_id=UUID(ticket_id),
            event_id=event_id,
            first_name=ticket_data.first_name,
            last_name=ticket_data.last_name,
            email=ticket_data.email,
            seat=ticket_data.seat,
        )

    async def unregister_ticket(self, ticket_id: UUID) -> None:
        ticket = await self.repository.get(ticket_id)

        if ticket is None:
            raise ValueError("Ticket not found")

        try:
            success = await self.client.unregister(
                event_id=str(ticket.event_id),
                ticket_id=str(ticket.ticket_id),
            )
        except Exception as exc:
            raise RuntimeError("Failed to unregister ticket") from exc

        if not success:
            raise ValueError("Ticket was not unregistered")

        await self.repository.delete(ticket)
