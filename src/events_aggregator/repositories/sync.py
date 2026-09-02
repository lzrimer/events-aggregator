from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from events_aggregator.models import SyncMetadata, SyncStatus


class SyncRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self) -> SyncMetadata | None:
        result = await self.session.execute(
            select(SyncMetadata).order_by(SyncMetadata.id).limit(1)
        )

        return result.scalar_one_or_none()

    async def save(
        self,
        last_sync_time: datetime,
        last_changed_at: datetime | None,
        sync_status: SyncStatus,
    ) -> SyncMetadata:
        metadata = await self.get()

        if metadata is None:
            metadata = SyncMetadata(
                last_sync_time=last_sync_time,
                last_changed_at=last_changed_at,
                sync_status=sync_status,
            )
            self.session.add(metadata)
        else:
            metadata.last_sync_time = last_sync_time
            metadata.last_changed_at = last_changed_at
            metadata.sync_status = sync_status

        await self.session.commit()
        await self.session.refresh(metadata)

        return metadata
