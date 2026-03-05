import pytest
from httpx import AsyncClient
import jwt
from backend.app.config import settings

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
async def test_successful_register(client: AsyncClient):
    register_response = await client.post(
        "/users",
        json=TEST_USER_DATA,
    )

    assert register_response.status_code == 200


@pytest.mark.anyio
async def test_successful_login(client: AsyncClient):
    register_response = await client.post(
        "/users",
        json=TEST_USER_DATA,
    )

    assert register_response.status_code == 200

    login_response = await client.post(
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

    decoded_token = jwt.decode(
        token_data["access_token"], settings.SECRET_KEY, algorithms=settings.ALGORITHM
    )
    assert decoded_token["sub"] == TEST_USER_DATA["login"]
    assert "exp" in decoded_token


@pytest.mark.anyio
async def test_login_with_incorrect_password(client: AsyncClient):
    register_response = await client.post(
        "/users",
        json=TEST_USER_DATA,
    )

    assert register_response.status_code == 200

    login_response = await client.post(
        "/token",
        data={
            "username": TEST_USER_DATA["login"],
            "password": "WrongPassword123!",
        },
    )

    assert login_response.status_code == 401


@pytest.mark.anyio
async def test_login_with_nonexistent_user(client: AsyncClient):
    register_response = await client.post(
        "/users",
        json=TEST_USER_DATA,
    )

    assert register_response.status_code == 200

    login_response = await client.post(
        "/token",
        data={
            "username": "NonExistUser",
            "password": TEST_USER_DATA["password"],
        },
    )

    assert login_response.status_code == 401


@pytest.mark.anyio
async def test_login_with_emptycreds(client: AsyncClient):
    register_response = await client.post(
        "/users",
        json=TEST_USER_DATA,
    )

    assert register_response.status_code == 200

    login_response = await client.post(
        "/token",
        data={
            "username": None,
            "password": None,
        },
    )

    assert login_response.status_code == 422


@pytest.mark.anyio
async def test_different_tokens(client: AsyncClient):
    register_response = await client.post(
        "/users",
        json=TEST_USER_DATA,
    )
    assert register_response.status_code == 200

    login_response_1 = await client.post(
        "/token",
        data={
            "username": TEST_USER_DATA["login"],
            "password": TEST_USER_DATA["password"],
        },
    )
    assert login_response_1.status_code == 200
    token_1 = login_response_1.json()["access_token"]

    login_response_2 = await client.post(
        "/token",
        data={
            "username": TEST_USER_DATA["login"],
            "password": TEST_USER_DATA["password"],
        },
    )
    assert login_response_2.status_code == 200
    token_2 = login_response_2.json()["access_token"]

    decoded_token_1 = jwt.decode(
        token_1,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    decoded_token_2 = jwt.decode(
        token_2,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    assert decoded_token_1["sub"] == decoded_token_2["sub"]
    assert token_1 != token_2
