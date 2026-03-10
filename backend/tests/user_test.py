import pytest
from httpx import AsyncClient
from backend.tests.utils import create_user_and_get_token

TEST_USER_DATA = {
    "login": "test",
    "email": "test@mail.ru",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "last_name": "Test",
    "first_name": "User",
    "patronymic": "Test",
}
TEST_USER_DATA2 = {
    "login": "test2",
    "email": "test2@mail.ru",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "last_name": "Test2",
    "first_name": "User2",
    "patronymic": "Test2",
}


@pytest.mark.anyio
async def test_root(client: AsyncClient):
    response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


@pytest.mark.anyio
async def test_get_me(client: AsyncClient):
    user = await create_user_and_get_token(client)

    get_me_response = await client.get("/users/me", headers=user["headers"])

    assert get_me_response.status_code == 200


@pytest.mark.anyio
async def test_get_all_users(client: AsyncClient):
    await create_user_and_get_token(client)
    await create_user_and_get_token(client)

    all_users_response = await client.get("/users")
    users_list = all_users_response.json()

    assert len(users_list) == 2


@pytest.mark.anyio
async def test_get_user_by_id(client: AsyncClient):
    user = await create_user_and_get_token(client)

    get_user_response = await client.get(f"/users/{user['user']['id']}")
    assert get_user_response.status_code == 200
    get_user_data = get_user_response.json()

    assert user["user"]["login"] == get_user_data["login"]
