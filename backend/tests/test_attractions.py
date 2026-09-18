"""The catalogue, and joining a queue."""

from httpx import AsyncClient

from tests.conftest import needs_handler
from tests.seed import KAIO_PALACE

# Exactly what `GET /attractions/` publishes: the attraction, and nothing about the caller.
ATTRACTION_FIELDS = {"id", "name", "photo_url", "max_people", "people_inside", "avg_duration"}


class TestListAttractions:
    @needs_handler
    async def test_returns_the_attractions_and_only_their_own_fields(
        self, client: AsyncClient, visitor: dict[str, str]
    ):
        response = await client.get("/attractions/", headers=visitor)
        assert response.status_code == 200
        attractions = response.json()
        assert [a["name"] for a in attractions] == [
            "La Salle du Temps",
            "Le Vaisseau de Freezer",
            "Le Palais de Kaio",
        ]
        assert set(attractions[0]) == ATTRACTION_FIELDS
        assert attractions[0]["avg_duration"] == 120
        assert attractions[0]["people_inside"] == 12

    async def test_refuses_without_a_token(self, client: AsyncClient):
        response = await client.get("/attractions/")
        assert response.status_code == 400

    async def test_refuses_a_forged_token(self, client: AsyncClient, forged: dict[str, str]):
        response = await client.get("/attractions/", headers=forged)
        assert response.status_code == 400


class TestJoinQueue:
    @needs_handler
    async def test_takes_a_place_in_the_queue(self, client: AsyncClient, visitor: dict[str, str]):
        response = await client.post(f"/attractions/{KAIO_PALACE}/queue/join/", headers=visitor)
        assert response.status_code == 200

    @needs_handler
    async def test_refuses_an_attraction_that_does_not_exist(
        self, client: AsyncClient, visitor: dict[str, str]
    ):
        response = await client.post("/attractions/999/queue/join/", headers=visitor)
        assert response.status_code == 400

    async def test_refuses_without_a_token(self, client: AsyncClient):
        response = await client.post(f"/attractions/{KAIO_PALACE}/queue/join/")
        assert response.status_code == 400
