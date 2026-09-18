"""The operations console: staff only, and it must not admit that it exists."""

from httpx import AsyncClient

from tests.conftest import needs_handler
from tests.seed import ENTRY_GOKU_READY, ENTRY_READY_ON_FULL


class TestConsoleRows:
    @needs_handler
    async def test_lists_every_attraction_with_who_has_been_called(
        self, client: AsyncClient, staff: dict[str, str]
    ):
        response = await client.get("/console/", headers=staff)
        assert response.status_code == 200
        rows = response.json()
        assert len(rows) == 3
        called = {row["attraction"]["name"]: len(row["ready"]) for row in rows}
        # An attraction with nobody called is still returned, with an empty list.
        assert called == {
            "La Salle du Temps": 0,
            "Le Vaisseau de Freezer": 1,
            "Le Palais de Kaio": 2,
        }

    async def test_a_visitor_is_refused(self, client: AsyncClient, visitor: dict[str, str]):
        response = await client.get("/console/", headers=visitor)
        assert response.status_code == 400

    async def test_refuses_without_a_token(self, client: AsyncClient):
        response = await client.get("/console/")
        assert response.status_code == 400


class TestAcceptEntry:
    @needs_handler
    async def test_lets_the_visitor_in(self, client: AsyncClient, staff: dict[str, str]):
        response = await client.post(
            f"/console/entries/{ENTRY_GOKU_READY}/accept/", headers=staff
        )
        assert response.status_code == 200

    @needs_handler
    async def test_refuses_when_the_attraction_is_full(
        self, client: AsyncClient, staff: dict[str, str]
    ):
        response = await client.post(
            f"/console/entries/{ENTRY_READY_ON_FULL}/accept/", headers=staff
        )
        assert response.status_code == 400

    async def test_a_visitor_cannot_accept_their_own_place(
        self, client: AsyncClient, visitor: dict[str, str]
    ):
        response = await client.post(
            f"/console/entries/{ENTRY_GOKU_READY}/accept/", headers=visitor
        )
        assert response.status_code == 400


class TestRefuseEntry:
    @needs_handler
    async def test_removes_the_place(self, client: AsyncClient, staff: dict[str, str]):
        response = await client.post(
            f"/console/entries/{ENTRY_GOKU_READY}/refuse/", headers=staff
        )
        assert response.status_code == 200

    @needs_handler
    async def test_refuses_a_place_that_does_not_exist(
        self, client: AsyncClient, staff: dict[str, str]
    ):
        response = await client.post("/console/entries/999/refuse/", headers=staff)
        assert response.status_code == 400

    async def test_a_visitor_is_refused(self, client: AsyncClient, visitor: dict[str, str]):
        response = await client.post(
            f"/console/entries/{ENTRY_GOKU_READY}/refuse/", headers=visitor
        )
        assert response.status_code == 400
