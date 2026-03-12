from httpx import AsyncClient
from uuid import uuid4
import random


async def create_user_and_get_token(
    client: AsyncClient, **user_data
) -> dict[str : str | dict]:
    rand_uuid = str(uuid4())[:8]
    random_data = {
        "login": f"test{rand_uuid}",
        "email": f"test{rand_uuid}@mail.ru",
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


# Держать во внимании, что эти ф-ии могут создавать уже существующие приоритеты и статусы, что может возвращать ошибки
async def create_priority(client: AsyncClient, priority: str | None = None):
    priorities = ["Низкий", "Средний", "Высокий", "Блокирующий"]
    create_response = await client.post(
        "/priorities",
        json={"title": random.choice(priorities) if not priority else priority},
    )
    assert create_response.status_code == 200
    return create_response.json()


async def create_status(client: AsyncClient, status: str | None = None):
    statuses = [
        "Открыт",
        "Добавлен в план",
        "Информация получена",
        "В работе",
        "Ожидаем информацию",
        "Грумминг",
        "Предварительная модерация",
        "Демонстрация заказчику",
        "Закрыт",
    ]
    create_response = await client.post(
        "/statuses",
        json={"title": random.choice(statuses) if not status else status},
    )
    assert create_response.status_code == 200
    return create_response.json()
