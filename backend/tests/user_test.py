import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_root(client: AsyncClient):
    response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


@pytest.mark.anyio
async def test_login_user(client: AsyncClient):
    response = await client.get(
        "/users", json={"login": "zzzatoox", "password": "Qwerty123!"}
    )

    assert response.status_code == 200
