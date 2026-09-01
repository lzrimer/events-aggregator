from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from events_aggregator.models import Event


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
        count_query = select(func.count(Event.id))

        if date_from is not None:
            query = query.where(Event.event_time >= date_from)
            count_query = count_query.where(Event.event_time >= date_from)

        count_result = await self.session.execute(count_query)
        count = count_result.scalar_one()

        result = await self.session.execute(
            query.order_by(Event.event_time).offset(offset).limit(limit)
        )

        return list(result.scalars().all()), count
