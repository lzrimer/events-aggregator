from unittest.mock import AsyncMock

import pytest

from events_aggregator.clients import EventsPaginator


@pytest.mark.asyncio
async def test_paginator_returns_events_from_all_pages():
    client = AsyncMock()

    client.events.return_value = {
        "next": "http://events-provider.test/api/events/?cursor=abc",
        "results": [
            {"id": "event-1", "name": "First event"},
            {"id": "event-2", "name": "Second event"},
        ],
    }

    client.events_page.return_value = {
        "next": None,
        "results": [
            {"id": "event-3", "name": "Third event"},
        ],
    }

    paginator = EventsPaginator(
        client=client,
        changed_at="2000-01-01",
    )

    events = [event async for event in paginator]

    assert events == [
        {"id": "event-1", "name": "First event"},
        {"id": "event-2", "name": "Second event"},
        {"id": "event-3", "name": "Third event"},
    ]

    client.events.assert_awaited_once_with("2000-01-01")

    client.events_page.assert_awaited_once_with(
        "http://events-provider.test/api/events/?cursor=abc"
    )


@pytest.mark.asyncio
async def test_paginator_stops_when_next_is_none():
    client = AsyncMock()

    client.events.return_value = {
        "next": None,
        "results": [
            {"id": "event-1", "name": "First event"},
        ],
    }

    paginator = EventsPaginator(
        client=client,
        changed_at="2000-01-01",
    )

    events = [event async for event in paginator]

    assert events == [
        {"id": "event-1", "name": "First event"},
    ]

    client.events.assert_awaited_once_with("2000-01-01")
    client.events_page.assert_not_awaited()
