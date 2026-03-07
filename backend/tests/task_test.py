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

TEST_TASK_DATA = {"title": "test", "owner_id": 1, "priority_id": 1, "status_id": 1}


@pytest.mark.anyio
async def test_get_all_tasks(client: AsyncClient):
    tasks_response = await client.get("/tasks")
    assert tasks_response.status_code == 200
    tasks_data = tasks_response.json()
    assert len(tasks_data) == 0

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

    priority_response = await client.post("/priorities", json={"title": "Низкий"})
    assert priority_response.status_code == 200

    status_response = await client.post("/statuses", json={"title": "Открыт"})
    assert status_response.status_code == 200

    task_response = await client.post("/tasks", json=TEST_TASK_DATA)
    assert task_response.status_code == 200

    tasks_response = await client.get("/tasks")
    assert tasks_response.status_code == 200

    tasks_data = tasks_response.json()
    assert len(tasks_data) == 1


@pytest.mark.anyio
async def test_create_task(client: AsyncClient):
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

    priority_response = await client.post("/priorities", json={"title": "Низкий"})
    assert priority_response.status_code == 200

    status_response = await client.post("/statuses", json={"title": "Открыт"})
    assert status_response.status_code == 200

    task_response = await client.post("/tasks", json=TEST_TASK_DATA)
    assert task_response.status_code == 200

    task_data = task_response.json()
    assert task_data["title"] == TEST_TASK_DATA["title"]
    assert task_data["owner_id"] == TEST_TASK_DATA["owner_id"]
    assert task_data["priority_id"] == TEST_TASK_DATA["priority_id"]
    assert task_data["status_id"] == TEST_TASK_DATA["status_id"]


@pytest.mark.anyio
async def test_get_task_by_id(client: AsyncClient):
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

    priority_response = await client.post("/priorities", json={"title": "Низкий"})
    assert priority_response.status_code == 200

    status_response = await client.post("/statuses", json={"title": "Открыт"})
    assert status_response.status_code == 200

    task_create_response = await client.post("/tasks", json=TEST_TASK_DATA)
    assert task_create_response.status_code == 200
    task_data = task_create_response.json()

    task_response = await client.get(f"/tasks/{task_data['id']}")
    assert task_response.status_code == 200

    task_data2 = task_response.json()
    assert task_data["id"] == task_data2["id"]


@pytest.mark.anyio
async def test_update_task(client: AsyncClient):
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

    priority_response = await client.post("/priorities", json={"title": "Низкий"})
    assert priority_response.status_code == 200

    status_response = await client.post("/statuses", json={"title": "Открыт"})
    assert status_response.status_code == 200

    task_create_response = await client.post("/tasks", json=TEST_TASK_DATA)
    assert task_create_response.status_code == 200
    task_data = task_create_response.json()

    task_data["title"] = "test2"

    task_update_response = await client.put(f"/tasks/{task_data['id']}", json=task_data)
    assert task_update_response.status_code == 200

    updated_task_data = task_update_response.json()
    assert task_data["title"] == updated_task_data["title"]


@pytest.mark.anyio
async def test_delete_task(client: AsyncClient):
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

    priority_response = await client.post("/priorities", json={"title": "Низкий"})
    assert priority_response.status_code == 200

    status_response = await client.post("/statuses", json={"title": "Открыт"})
    assert status_response.status_code == 200

    task_create_response = await client.post("/tasks", json=TEST_TASK_DATA)
    assert task_create_response.status_code == 200
    task_data = task_create_response.json()

    task_delete_response = await client.delete(f"tasks/{task_data['id']}")
    assert task_delete_response.status_code == 200

    task_delete_response = await client.delete(f"tasks/{task_data['id']}")
    assert task_delete_response.status_code == 404
