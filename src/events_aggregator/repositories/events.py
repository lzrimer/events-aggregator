from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from events_aggregator.models import Event, Place


class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, event_id: UUID) -> Event | None:
        result = await self.session.execute(
            select(Event).options(selectinload(Event.place)).where(Event.id == event_id)
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
        date_from: datetime | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Event], int]:
        query = select(Event).options(selectinload(Event.place))

        if date_from:
            query = query.where(Event.event_time >= date_from)

        query = query.order_by(Event.event_time)

        count_query = select(Event.id)

        if date_from:
            count_query = count_query.where(Event.event_time >= date_from)

        count_result = await self.session.execute(count_query)
        count = len(count_result.all())

        result = await self.session.execute(query.offset(offset).limit(limit))

        return list(result.scalars().all()), count

    @staticmethod
    def _parse_datetime(
        value: datetime | str | None,
    ) -> datetime | None:
        if value is None:
            return None

        if isinstance(value, datetime):
            return value

        return datetime.fromisoformat(value)

    async def save_place(self, place_data: dict) -> Place:
        allowed_fields = {
            "id",
            "name",
            "city",
            "address",
            "seats_pattern",
            "changed_at",
            "created_at",
        }

        data = {
            key: value for key, value in place_data.items() if key in allowed_fields
        }

        data["changed_at"] = self._parse_datetime(data.get("changed_at"))

        data["created_at"] = self._parse_datetime(data.get("created_at"))

        place = await self.session.get(
            Place,
            data["id"],
        )

        if place is None:
            place = Place(**data)
            self.session.add(place)
        else:
            for key, value in data.items():
                setattr(place, key, value)

        return place

    async def save(self, event_data: dict) -> Event:
        event = await self.session.get(
            Event,
            event_data["id"],
        )

        place_data = event_data["place"]

        event_fields = {
            key: value
            for key, value in event_data.items()
            if key != "place" and key in Event.__table__.columns
        }

        for field in (
            "event_time",
            "registration_deadline",
            "changed_at",
            "created_at",
            "status_changed_at",
        ):
            if field in event_fields:
                event_fields[field] = self._parse_datetime(event_fields[field])

        place = await self.save_place(place_data)

        event_fields["place_id"] = place.id

        if event is None:
            event = Event(**event_fields)
            self.session.add(event)
        else:
            for key, value in event_fields.items():
                setattr(event, key, value)

        await self.session.commit()
        await self.session.refresh(event)

        return event
