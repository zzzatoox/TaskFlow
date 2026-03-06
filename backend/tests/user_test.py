import pytest
from httpx import AsyncClient

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
    reg_response = await client.post("/users", json=TEST_USER_DATA)

    assert reg_response.status_code == 200

    token_response = await client.post(
        "/token",
        data={
            "username": TEST_USER_DATA["login"],
            "password": TEST_USER_DATA["password"],
        },
    )

    assert token_response.status_code == 200
    token_data = token_response.json()
    assert "access_token" in token_data

    headers = {"Authorization": f"Bearer {token_data['access_token']}"}

    get_me_response = await client.get("/users/me", headers=headers)

    assert get_me_response.status_code == 200

    user_data = get_me_response.json()

    assert user_data["login"] == TEST_USER_DATA["login"]


@pytest.mark.anyio
async def test_get_all_users(client: AsyncClient):
    register_response1 = await client.post("/users", json=TEST_USER_DATA)
    assert register_response1.status_code == 200
    register_response2 = await client.post("/users", json=TEST_USER_DATA2)
    assert register_response2.status_code == 200

    user_data1 = register_response1.json()
    user_data2 = register_response2.json()

    all_users_response = await client.get("/users")
    users_list = all_users_response.json()

    assert len(users_list) == 2
    assert user_data1["login"] == users_list[0]["login"]
    assert user_data2["login"] == users_list[1]["login"]


@pytest.mark.anyio
async def test_get_user_by_id(client: AsyncClient):
    reg_response = await client.post("/users", json=TEST_USER_DATA)
    assert reg_response.status_code == 200

    user_data = reg_response.json()

    get_user_response = await client.get(f"/users/{user_data['id']}")
    assert get_user_response.status_code == 200
    get_user_data = get_user_response.json()

    assert user_data["login"] == get_user_data["login"]
