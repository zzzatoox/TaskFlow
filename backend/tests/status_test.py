from httpx import AsyncClient
import pytest


@pytest.mark.anyio
async def test_get_statuses(client: AsyncClient):
    create_response = await client.post("/statuses", json={"title": "В работе"})
    assert create_response.status_code == 200

    get_response = await client.get("/statuses")
    assert get_response.status_code == 200
    statuses = get_response.json()
    assert len(statuses) == 1


@pytest.mark.anyio
async def test_status_create(client: AsyncClient):
    create_response = await client.post("/statuses")
    assert create_response.status_code == 422
    create_response = await client.post("/statuses", json={"title": "В работе"})
    assert create_response.status_code == 200
    create_response = await client.post("/statuses", json={"title": "В работе"})
    assert create_response.status_code == 409


@pytest.mark.anyio
async def test_get_status_by_id(client: AsyncClient):
    create_response = await client.post("/statuses", json={"title": "В работе"})
    assert create_response.status_code == 200
    status = create_response.json()

    get_response = await client.get(f"/statuses/{status['id']}")
    assert get_response.status_code == 200

    get_response = await client.get("/statuses/123")
    assert get_response.status_code == 404


@pytest.mark.anyio
async def test_update_status(client: AsyncClient):
    create_response = await client.post("/statuses", json={"title": "В работе"})
    assert create_response.status_code == 200
    status = create_response.json()

    update_response = await client.put(
        f"/statuses/{status['id']}", json={"title": "В подтверждении"}
    )
    assert update_response.status_code == 200


@pytest.mark.anyio
async def test_delete_status(client: AsyncClient):
    create_response = await client.post("/statuses", json={"title": "В работе"})
    assert create_response.status_code == 200
    status = create_response.json()

    delete_response = await client.delete(f"/statuses/{status['id']}")
    assert delete_response.status_code == 200
