import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta, timezone
from backend.tests.utils import (
    create_user_and_get_token,
    create_priority,
    create_status,
)

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

TEST_TASK_DATA = {"title": "test", "owner_id": 1, "priority_id": 1, "status_id": 1}
priorities = ["Низкий", "Средний", "Высокий", "Блокирующий"]
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


@pytest.mark.anyio
async def test_get_all_tasks(client: AsyncClient):
    user = await create_user_and_get_token(client)
    task_data = TEST_TASK_DATA.copy()

    tasks_response = await client.get("/tasks", headers=user["headers"])
    assert tasks_response.status_code == 200
    tasks_data = tasks_response.json()
    assert len(tasks_data) == 0

    priority_response = await client.post("/priorities", json={"title": "Низкий"})
    assert priority_response.status_code == 200

    status_response = await client.post("/statuses", json={"title": "Открыт"})
    assert status_response.status_code == 200

    task_response = await client.post("/tasks", json=task_data)
    assert task_response.status_code == 401

    for _ in range(15):
        task_response = await client.post(
            "/tasks", headers=user["headers"], json=task_data
        )

    tasks_response = await client.get("/tasks", headers=user["headers"])
    assert tasks_response.status_code == 200

    tasks_data = tasks_response.json()
    assert len(tasks_data) == 10

    task_response = await client.get(
        "/tasks", headers=user["headers"], params={"skip": 10, "limit": 10}
    )
    tasks_data = task_response.json()

    assert len(tasks_data) <= 10


@pytest.mark.anyio
async def test_failure_filter_task_by_date(client: AsyncClient):
    user = await create_user_and_get_token(client)

    start = (datetime.now(timezone.utc) + timedelta(minutes=1)).isoformat()
    end = (datetime.now(timezone.utc) + timedelta(minutes=2)).isoformat()
    tasks_by_date = await client.get(
        "/tasks", headers=user["headers"], params={"start_date": start, "end_date": end}
    )
    assert tasks_by_date.status_code == 200
    tasks_by_date_data = tasks_by_date.json()
    assert len(tasks_by_date_data) == 0


@pytest.mark.anyio
async def test_failure_filter_task_by_priority(client: AsyncClient):
    user = await create_user_and_get_token(client)

    tasks_by_priority = await client.get(
        "/tasks", headers=user["headers"], params={"priority": "Низкий"}
    )
    assert tasks_by_priority.status_code == 200
    tasks_by_priority_data = tasks_by_priority.json()
    assert len(tasks_by_priority_data) == 0


@pytest.mark.anyio
async def test_failure_filter_task_by_status(client: AsyncClient):
    user = await create_user_and_get_token(client)

    tasks_by_status = await client.get(
        "/tasks", headers=user["headers"], params={"status": "Открыт"}
    )
    assert tasks_by_status.status_code == 200
    tasks_by_status_data = tasks_by_status.json()
    assert len(tasks_by_status_data) == 0


@pytest.mark.anyio
async def test_start_date_greater_than_end_date(client: AsyncClient):
    user = await create_user_and_get_token(client)

    start = (datetime.now(timezone.utc) + timedelta(minutes=1)).isoformat()
    end = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    tasks_by_date = await client.get(
        "/tasks", headers=user["headers"], params={"start_date": start, "end_date": end}
    )
    assert tasks_by_date.status_code == 422


@pytest.mark.anyio
async def test_invalid_date_format(client: AsyncClient):
    user = await create_user_and_get_token(client)

    tasks_by_date = await client.get(
        "/tasks", headers=user["headers"], params={"start_date": "invalid-date"}
    )
    assert tasks_by_date.status_code == 422

    tasks_by_date = await client.get(
        "/tasks", headers=user["headers"], params={"end_date": "invalid-date"}
    )
    assert tasks_by_date.status_code == 422


@pytest.mark.anyio
async def test_task_filter_by_date(client: AsyncClient):
    user = await create_user_and_get_token(client)
    task_data = TEST_TASK_DATA.copy()

    _ = await create_priority(client, "Низкий")
    _ = await create_status(client, "Открыт")

    ctr = await client.post("/tasks", headers=user["headers"], json=task_data)
    assert ctr.status_code == 200
    task = ctr.json()

    start = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    end = (datetime.now(timezone.utc) + timedelta(minutes=1)).isoformat()
    tr = await client.get(
        "/tasks", headers=user["headers"], params={"start_date": start, "end_date": end}
    )
    assert tr.status_code == 200
    tasks_by_date_data = tr.json()
    assert any(t["id"] == task["id"] for t in tasks_by_date_data)


@pytest.mark.anyio
async def test_task_filter_by_priority(client: AsyncClient):
    user = await create_user_and_get_token(client)
    task_data = TEST_TASK_DATA.copy()

    _ = await create_status(client, "Открыт")
    pr1 = await create_priority(client, "Низкий")
    pr2 = await create_priority(client, "Средний")

    task_data["priority_id"] = pr1["id"]
    ctr = await client.post("/tasks", headers=user["headers"], json=task_data)
    assert ctr.status_code == 200
    task_low = ctr.json()

    task_data["priority_id"] = pr2["id"]
    ctr = await client.post("/tasks", headers=user["headers"], json=task_data)
    assert ctr.status_code == 200

    tlr = await client.get(
        "/tasks", headers=user["headers"], params={"priority": "Низкий"}
    )
    assert tlr.status_code == 200
    task_low_get = tlr.json()

    assert len(task_low_get) == 1
    assert task_low_get[0]["id"] == task_low["id"]


@pytest.mark.anyio
async def test_task_filter_by_status(client: AsyncClient):
    user = await create_user_and_get_token(client)
    task_data = TEST_TASK_DATA.copy()

    _ = await create_priority(client, "Низкий")
    st1 = await create_status(client, "В работе")
    st2 = await create_status(client, "Завершен")

    task_data["status_id"] = st1["id"]
    ctr = await client.post("/tasks", headers=user["headers"], json=task_data)
    assert ctr.status_code == 200
    task_in_progress = ctr.json()

    task_data["status_id"] = st2["id"]
    ctr = await client.post("/tasks", headers=user["headers"], json=task_data)
    assert ctr.status_code == 200

    tr = await client.get(
        "/tasks", headers=user["headers"], params={"status": "В работе"}
    )
    assert tr.status_code == 200
    task_in_progress_get = tr.json()

    assert len(task_in_progress_get) == 1
    assert task_in_progress_get[0]["id"] == task_in_progress["id"]


@pytest.mark.anyio
async def test_create_task(client: AsyncClient):
    user = await create_user_and_get_token(client)
    task_payload = TEST_TASK_DATA.copy()

    priority_response = await client.post("/priorities", json={"title": "Низкий"})
    assert priority_response.status_code == 200

    status_response = await client.post("/statuses", json={"title": "Открыт"})
    assert status_response.status_code == 200

    task_response = await client.post("/tasks", json=task_payload)
    assert task_response.status_code == 401
    task_response = await client.post(
        "/tasks", headers=user["headers"], json=task_payload
    )
    assert task_response.status_code == 200

    created_task = task_response.json()
    assert created_task["title"] == task_payload["title"]
    assert created_task["owner_id"] == task_payload["owner_id"]
    assert created_task["priority_id"] == task_payload["priority_id"]
    assert created_task["status_id"] == task_payload["status_id"]


@pytest.mark.anyio
async def test_get_task_by_id(client: AsyncClient):
    user = await create_user_and_get_token(client)
    user2 = await create_user_and_get_token(client)
    task_data = TEST_TASK_DATA.copy()

    priority_response = await client.post("/priorities", json={"title": "Низкий"})
    assert priority_response.status_code == 200

    status_response = await client.post("/statuses", json={"title": "Открыт"})
    assert status_response.status_code == 200

    task_create_response = await client.post(
        "/tasks", headers=user["headers"], json=task_data
    )
    assert task_create_response.status_code == 200
    task_data = task_create_response.json()

    task_response = await client.get(
        f"/tasks/{task_data['id']}", headers=user2["headers"]
    )
    assert task_response.status_code == 403
    task_response = await client.get(
        f"/tasks/{task_data['id']}", headers=user["headers"]
    )
    assert task_response.status_code == 200

    task_data2 = task_response.json()
    assert task_data["id"] == task_data2["id"]


@pytest.mark.anyio
async def test_update_task(client: AsyncClient):
    user = await create_user_and_get_token(client)
    task_data = TEST_TASK_DATA.copy()

    priority_response = await client.post("/priorities", json={"title": "Низкий"})
    assert priority_response.status_code == 200

    status_response = await client.post("/statuses", json={"title": "Открыт"})
    assert status_response.status_code == 200

    task_create_response = await client.post(
        "/tasks", headers=user["headers"], json=task_data
    )
    assert task_create_response.status_code == 200
    task_data = task_create_response.json()

    task_data["title"] = "test2"

    task_update_response = await client.put(
        f"/tasks/{task_data['id']}", headers=user["headers"], json=task_data
    )
    assert task_update_response.status_code == 200

    updated_task_data = task_update_response.json()
    assert task_data["title"] == updated_task_data["title"]


@pytest.mark.anyio
async def test_delete_task(client: AsyncClient):
    user = await create_user_and_get_token(client)
    task_data = TEST_TASK_DATA.copy()

    priority_response = await client.post("/priorities", json={"title": "Низкий"})
    assert priority_response.status_code == 200

    status_response = await client.post("/statuses", json={"title": "Открыт"})
    assert status_response.status_code == 200

    task_create_response = await client.post("/tasks", json=task_data)
    assert task_create_response.status_code == 401
    task_create_response = await client.post(
        "/tasks", headers=user["headers"], json=task_data
    )
    assert task_create_response.status_code == 200
    task_data = task_create_response.json()

    task_delete_response = await client.delete(
        f"tasks/{task_data['id']}", headers=user["headers"]
    )
    assert task_delete_response.status_code == 200

    task_delete_response = await client.delete(
        f"tasks/{task_data['id']}", headers=user["headers"]
    )
    assert task_delete_response.status_code == 404
