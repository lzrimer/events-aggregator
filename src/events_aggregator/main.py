from fastapi import FastAPI

from events_aggregator.api.events import router as events_router
from events_aggregator.api.seats import router as seats_router
from events_aggregator.api.sync import router as sync_router
from events_aggregator.api.tickets import router as tickets_router

app = FastAPI(
    title="Events Aggregator",
)


app.include_router(events_router)
app.include_router(seats_router)
app.include_router(sync_router)
app.include_router(tickets_router)


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
