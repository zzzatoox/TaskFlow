from httpx import AsyncClient
import pytest


@pytest.mark.anyio
async def test_get_priorities(client: AsyncClient):
    create_response = await client.post("/priorities", json={"title": "Низкий"})
    assert create_response.status_code == 200

    get_response = await client.get("/priorities")
    assert get_response.status_code == 200
    priorities = get_response.json()
    assert len(priorities) == 1


@pytest.mark.anyio
async def test_priority_create(client: AsyncClient):
    create_response = await client.post("/priorities")
    assert create_response.status_code == 422
    create_response = await client.post("/priorities", json={"title": "Низкий"})
    assert create_response.status_code == 200
    create_response = await client.post("/priorities", json={"title": "Низкий"})
    assert create_response.status_code == 409


@pytest.mark.anyio
async def test_get_priority_by_id(client: AsyncClient):
    create_response = await client.post("/priorities", json={"title": "Низкий"})
    assert create_response.status_code == 200
    priority = create_response.json()

    get_response = await client.get(f"/priorities/{priority['id']}")
    assert get_response.status_code == 200

    get_response = await client.get("/priorities/123")
    assert get_response.status_code == 404


@pytest.mark.anyio
async def test_update_priority(client: AsyncClient):
    create_response = await client.post("/priorities", json={"title": "Низкий"})
    assert create_response.status_code == 200
    priority = create_response.json()

    update_response = await client.put(
        f"/priorities/{priority['id']}", json={"title": "Средний"}
    )
    assert update_response.status_code == 200


@pytest.mark.anyio
async def test_delete_status(client: AsyncClient):
    create_response = await client.post("/priorities", json={"title": "Низкий"})
    assert create_response.status_code == 200
    priority = create_response.json()

    delete_response = await client.delete(f"/priorities/{priority['id']}")
    assert delete_response.status_code == 200
