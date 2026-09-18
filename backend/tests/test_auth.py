"""Accounts: the three routes that are actually implemented."""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.seed import PASSWORD


class TestSignup:
    async def test_creates_the_account_and_returns_a_token(self, client: AsyncClient):
        response = await client.post(
            "/auth/signup/",
            json={
                "username": "krilin",
                "email": "krilin@dbz.fr",
                "password1": "destructo-disc",
                "password2": "destructo-disc",
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["user"] == {"id": 4, "username": "krilin", "is_staff": False}
        assert body["token"]

    async def test_refuses_two_different_passwords(self, client: AsyncClient):
        response = await client.post(
            "/auth/signup/",
            json={
                "username": "krilin",
                "email": "krilin@dbz.fr",
                "password1": "destructo-disc",
                "password2": "destructo-disk",
            },
        )
        assert response.status_code == 400

    async def test_refuses_a_username_already_taken(self, client: AsyncClient):
        response = await client.post(
            "/auth/signup/",
            json={
                "username": "goku",
                "email": "other@dbz.fr",
                "password1": "kamehameha",
                "password2": "kamehameha",
            },
        )
        assert response.status_code == 400


class TestLogin:
    async def test_returns_a_token_for_the_right_password(self, client: AsyncClient):
        response = await client.post(
            "/auth/login/", json={"username": "goku", "password": PASSWORD}
        )
        assert response.status_code == 200
        assert response.json()["user"]["username"] == "goku"

    async def test_wrong_password_and_unknown_account_are_indistinguishable(
        self, client: AsyncClient
    ):
        wrong = await client.post(
            "/auth/login/", json={"username": "goku", "password": "not-it"}
        )
        unknown = await client.post(
            "/auth/login/", json={"username": "broly", "password": "not-it"}
        )
        assert wrong.status_code == unknown.status_code == 400
        # The whole point: the answer must never confirm that an account exists.
        assert wrong.json()["detail"] == unknown.json()["detail"]

    async def test_refuses_a_body_without_a_password(self, client: AsyncClient):
        response = await client.post("/auth/login/", json={"username": "goku"})
        assert response.status_code == 400
        assert "password" in response.json()["detail"]


class TestMe:
    async def test_returns_the_account_behind_the_token(
        self, client: AsyncClient, visitor: dict[str, str]
    ):
        response = await client.get("/auth/me/", headers=visitor)
        assert response.status_code == 200
        assert response.json() == {"id": 1, "username": "goku", "is_staff": False}

    async def test_refuses_without_a_token(self, client: AsyncClient):
        response = await client.get("/auth/me/")
        assert response.status_code == 400

    async def test_refuses_a_forged_token(self, client: AsyncClient, forged: dict[str, str]):
        response = await client.get("/auth/me/", headers=forged)
        assert response.status_code == 400
