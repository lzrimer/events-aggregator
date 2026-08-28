from typing import Any

import httpx


class EventsProviderClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _headers(self) -> dict[str, str]:
        return {
            "x-api-key": self.api_key,
        }

    async def events(self, changed_at: str | None) -> dict[str, Any]:
        url = f"{self.base_url}/api/events/"

        params = {}
        if changed_at:
            params["changed_at"] = changed_at

        async with httpx.AsyncClient(
            follow_redirects=True,
        ) as client:
            response = await client.get(
                url,
                params=params,
                headers=self._headers(),
            )
            response.raise_for_status()

        return response.json()

    async def events_page(self, url: str) -> dict[str, Any]:
        async with httpx.AsyncClient(
            follow_redirects=True,
        ) as client:
            response = await client.get(
                url,
                headers=self._headers(),
            )
            response.raise_for_status()

        return response.json()

    async def seats(self, event_id: str) -> list[str]:
        url = f"{self.base_url}/api/events/{event_id}/seats/"

        async with httpx.AsyncClient(
            follow_redirects=True,
        ) as client:
            response = await client.get(
                url,
                headers=self._headers(),
            )
            response.raise_for_status()

        return response.json()["seats"]

    async def register(
        self,
        event_id: str,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
    ) -> str:
        url = f"{self.base_url}/api/events/{event_id}/register/"

        data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "seat": seat,
        }

        async with httpx.AsyncClient(
            follow_redirects=True,
        ) as client:
            response = await client.post(
                url,
                json=data,
                headers=self._headers(),
            )

            print("REGISTER STATUS:", response.status_code)
            print("REGISTER RESPONSE:", response.text)

            response.raise_for_status()

        return response.json()["ticket_id"]

    async def unregister(
        self,
        event_id: str,
        ticket_id: str,
    ) -> bool:
        url = f"{self.base_url}/api/events/{event_id}/unregister/"

        data = {
            "ticket_id": ticket_id,
        }

        async with httpx.AsyncClient(
            follow_redirects=True,
        ) as client:
            response = await client.request(
                "DELETE",
                url,
                json=data,
                headers=self._headers(),
            )
            response.raise_for_status()

        return response.json()["success"]
