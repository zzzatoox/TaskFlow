import pytest
from httpx import AsyncClient, ASGITransport

from backend.app.main import app

BASE_URL = "http://testserver"

TEST_USER_DATA = {
    "login": "test",
    "email": "test@mail.ru",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "last_name": "Test",
    "first_name": "User",
    "patronymic": "Test",
}


@pytest.mark.anyio
async def test_successful_register():
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
        register_response = await ac.post(
            "/users",
            json=TEST_USER_DATA,
        )

        assert register_response.status_code == 200


@pytest.mark.anyio
async def test_successful_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
        register_response = await ac.post(
            "/users",
            json=TEST_USER_DATA,
        )

        assert register_response.status_code == 200

        login_response = await ac.post(
            "/token",
            data={
                "username": TEST_USER_DATA["login"],
                "password": TEST_USER_DATA["password"],
            },
        )

        assert login_response.status_code == 200
        token_data = login_response.json()

        assert "access_token" in token_data
        assert "token_type" in token_data
        assert token_data["token_type"] == "bearer"
