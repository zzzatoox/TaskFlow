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

TEST_TASK_DATA = {"title": "test", "owner_id": 1, "priority_id": 1, "status_id": 1}


@pytest.mark.anyio
async def test_get_all_tasks(client: AsyncClient):
    user = await create_user_and_get_token(client)

    tasks_response = await client.get("/tasks", headers=user["headers"])
    assert tasks_response.status_code == 200
    tasks_data = tasks_response.json()
    assert len(tasks_data) == 0

    priority_response = await client.post("/priorities", json={"title": "Низкий"})
    assert priority_response.status_code == 200

    status_response = await client.post("/statuses", json={"title": "Открыт"})
    assert status_response.status_code == 200

    task_response = await client.post("/tasks", json=TEST_TASK_DATA)
    assert task_response.status_code == 401
    task_response = await client.post(
        "/tasks", headers=user["headers"], json=TEST_TASK_DATA
    )
    assert task_response.status_code == 200

    tasks_response = await client.get("/tasks", headers=user["headers"])
    assert tasks_response.status_code == 200

    tasks_data = tasks_response.json()
    assert len(tasks_data) == 1


@pytest.mark.anyio
async def test_create_task(client: AsyncClient):
    user = await create_user_and_get_token(client)

    priority_response = await client.post("/priorities", json={"title": "Низкий"})
    assert priority_response.status_code == 200

    status_response = await client.post("/statuses", json={"title": "Открыт"})
    assert status_response.status_code == 200

    task_response = await client.post("/tasks", json=TEST_TASK_DATA)
    assert task_response.status_code == 401
    task_response = await client.post(
        "/tasks", headers=user["headers"], json=TEST_TASK_DATA
    )
    assert task_response.status_code == 200

    task_data = task_response.json()
    assert task_data["title"] == TEST_TASK_DATA["title"]
    assert task_data["owner_id"] == TEST_TASK_DATA["owner_id"]
    assert task_data["priority_id"] == TEST_TASK_DATA["priority_id"]
    assert task_data["status_id"] == TEST_TASK_DATA["status_id"]


@pytest.mark.anyio
async def test_get_task_by_id(client: AsyncClient):
    user = await create_user_and_get_token(client)
    user2 = await create_user_and_get_token(client)

    priority_response = await client.post("/priorities", json={"title": "Низкий"})
    assert priority_response.status_code == 200

    status_response = await client.post("/statuses", json={"title": "Открыт"})
    assert status_response.status_code == 200

    task_create_response = await client.post(
        "/tasks", headers=user["headers"], json=TEST_TASK_DATA
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

    priority_response = await client.post("/priorities", json={"title": "Низкий"})
    assert priority_response.status_code == 200

    status_response = await client.post("/statuses", json={"title": "Открыт"})
    assert status_response.status_code == 200

    task_create_response = await client.post(
        "/tasks", headers=user["headers"], json=TEST_TASK_DATA
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

    priority_response = await client.post("/priorities", json={"title": "Низкий"})
    assert priority_response.status_code == 200

    status_response = await client.post("/statuses", json={"title": "Открыт"})
    assert status_response.status_code == 200

    task_create_response = await client.post("/tasks", json=TEST_TASK_DATA)
    assert task_create_response.status_code == 401
    task_create_response = await client.post(
        "/tasks", headers=user["headers"], json=TEST_TASK_DATA
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
