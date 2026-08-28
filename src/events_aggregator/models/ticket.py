from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from events_aggregator.models.base import Base

if TYPE_CHECKING:
    from events_aggregator.models.event import Event


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    ticket_id: Mapped[UUID] = mapped_column()
    event_id: Mapped[UUID] = mapped_column(
        ForeignKey("events.id"),
    )
    first_name: Mapped[str] = mapped_column(
        String(100),
    )
    last_name: Mapped[str] = mapped_column(
        String(100),
    )
    email: Mapped[str] = mapped_column(
        String(255),
    )
    seat: Mapped[str] = mapped_column(
        String(50),
    )

    event: Mapped["Event"] = relationship(
        back_populates="tickets",
    )
