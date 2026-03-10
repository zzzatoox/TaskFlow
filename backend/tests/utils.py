from httpx import AsyncClient
from random import randint


async def create_user_and_get_token(
    client: AsyncClient, **user_data
) -> dict[str : str | dict]:
    random_data = {
        "login": f"test{randint(1, 10000)}",
        "email": f"test{randint(1, 10000)}@mail.ru",
        "password": "TestPassword123!",
        "password_confirm": "TestPassword123!",
        "last_name": "Test",
        "first_name": "User",
        "patronymic": "Test",
    }
    random_data.update(user_data)
    register_response = await client.post(
        "/users",
        json=random_data,
    )
    assert register_response.status_code == 200
    user = register_response.json()
    login_response = await client.post(
        "/token",
        data={
            "username": random_data["login"],
            "password": random_data["password"],
        },
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}

    return {"user": user, "token": token_data["access_token"], "headers": headers}
