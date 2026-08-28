from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from events_aggregator.api.events import router as events_router
from events_aggregator.api.sync import router as sync_router
from events_aggregator.api.tickets import router as tickets_router
from events_aggregator.core.database import create_tables, get_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(
    title="Events Aggregator",
    lifespan=lifespan,
)


app.include_router(events_router)
app.include_router(sync_router)
app.include_router(tickets_router)


@app.get("/api/health")
async def health_check():
    async for session in get_session():
        await session.execute(text("SELECT 1"))

    return {"status": "ok"}
