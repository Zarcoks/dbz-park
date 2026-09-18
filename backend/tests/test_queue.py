"""Places held in a queue: position, withdrawal, validation."""

from httpx import AsyncClient

from tests.conftest import needs_handler
from tests.seed import ENTRY_GOKU_READY, ENTRY_GOKU_WAITING, ENTRY_VEGETA_WAITING


class TestPosition:
    @needs_handler
    async def test_counts_the_people_ahead_including_this_place(
        self, client: AsyncClient, visitor: dict[str, str]
    ):
        response = await client.get(f"/queue/{ENTRY_GOKU_WAITING}/position/", headers=visitor)
        assert response.status_code == 200
        # goku joined the Time Room first: he is next in line.
        assert response.json() == {"position": 1}

    @needs_handler
    async def test_a_place_that_is_not_yours_is_refused(
        self, client: AsyncClient, visitor: dict[str, str]
    ):
        response = await client.get(f"/queue/{ENTRY_VEGETA_WAITING}/position/", headers=visitor)
        assert response.status_code == 400

    async def test_refuses_without_a_token(self, client: AsyncClient):
        response = await client.get(f"/queue/{ENTRY_GOKU_WAITING}/position/")
        assert response.status_code == 400


class TestLeaveQueue:
    @needs_handler
    async def test_releases_the_place(self, client: AsyncClient, visitor: dict[str, str]):
        response = await client.post(f"/queue/{ENTRY_GOKU_WAITING}/leave/", headers=visitor)
        assert response.status_code == 200

    @needs_handler
    async def test_refuses_a_place_that_does_not_exist(
        self, client: AsyncClient, visitor: dict[str, str]
    ):
        response = await client.post("/queue/999/leave/", headers=visitor)
        assert response.status_code == 400

    async def test_refuses_without_a_token(self, client: AsyncClient):
        response = await client.post(f"/queue/{ENTRY_GOKU_WAITING}/leave/")
        assert response.status_code == 400


class TestValidateQueueEntry:
    @needs_handler
    async def test_lets_a_called_visitor_in(self, client: AsyncClient, visitor: dict[str, str]):
        response = await client.post(f"/queue/{ENTRY_GOKU_READY}/validate/", headers=visitor)
        assert response.status_code == 200

    @needs_handler
    async def test_refuses_a_turn_that_has_not_come(
        self, client: AsyncClient, visitor: dict[str, str]
    ):
        response = await client.post(f"/queue/{ENTRY_GOKU_WAITING}/validate/", headers=visitor)
        assert response.status_code == 400

    async def test_refuses_without_a_token(self, client: AsyncClient):
        response = await client.post(f"/queue/{ENTRY_GOKU_READY}/validate/")
        assert response.status_code == 400
