from backend.app.main import app

from httpx import AsyncClient, ASGITransport
import pytest

BASE_URL = "http://testserver"


@pytest.mark.anyio
async def test_root():
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
        response = await ac.get("/")

    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


@pytest.mark.anyio
async def test_login_user():
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
        response = await ac.get(
            "/users", json={"login": "zzzatoox", "password": "Qwerty123!"}
        )

    assert response.status_code == 200
