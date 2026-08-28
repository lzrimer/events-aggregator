from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from events_aggregator.clients import EventsProviderClient


@pytest.mark.asyncio
async def test_get_events():
    client = EventsProviderClient(
        base_url="http://events-provider.test",
        api_key="test-key",
    )

    response_data = {
        "next": "http://events-provider.test/api/events/?cursor=abc",
        "previous": None,
        "results": [
            {
                "id": "event-1",
                "name": "Python Meetup",
            }
        ],
    }

    mock_response = MagicMock()
    mock_response.json.return_value = response_data

    with patch(
        "httpx.AsyncClient.get",
        new_callable=AsyncMock,
        return_value=mock_response,
    ) as mock_get:
        result = await client.events("2000-01-01")

    assert result == response_data
    mock_get.assert_awaited_once()
    assert mock_get.call_args.kwargs["params"] == {"changed_at": "2000-01-01"}


@pytest.mark.asyncio
async def test_get_seats():
    client = EventsProviderClient(
        base_url="http://events-provider.test",
        api_key="test-key",
    )

    mock_response = MagicMock()
    mock_response.json.return_value = {"seats": ["A1", "A3", "A4"]}

    with patch(
        "httpx.AsyncClient.get",
        new_callable=AsyncMock,
        return_value=mock_response,
    ) as mock_get:
        result = await client.seats("event-1")

    assert result == ["A1", "A3", "A4"]
    mock_get.assert_awaited_once()


@pytest.mark.asyncio
async def test_register():
    client = EventsProviderClient(
        base_url="http://events-provider.test",
        api_key="test-key",
    )

    mock_response = MagicMock()
    mock_response.json.return_value = {"ticket_id": "ticket-123"}

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock,
        return_value=mock_response,
    ) as mock_post:
        result = await client.register(
            event_id="event-1",
            first_name="Иван",
            last_name="Иванов",
            email="ivan@example.com",
            seat="A15",
        )

    assert result == "ticket-123"

    mock_post.assert_awaited_once()
    assert mock_post.call_args.kwargs["json"] == {
        "first_name": "Иван",
        "last_name": "Иванов",
        "email": "ivan@example.com",
        "seat": "A15",
    }


@pytest.mark.asyncio
async def test_unregister():
    client = EventsProviderClient(
        base_url="http://events-provider.test",
        api_key="test-key",
    )

    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True}

    with patch(
        "httpx.AsyncClient.request",
        new_callable=AsyncMock,
        return_value=mock_response,
    ) as mock_request:
        result = await client.unregister(
            event_id="event-1",
            ticket_id="ticket-123",
        )

    assert result is True

    mock_request.assert_awaited_once()
    assert mock_request.call_args.args[0] == "DELETE"
    assert mock_request.call_args.kwargs["json"] == {"ticket_id": "ticket-123"}
