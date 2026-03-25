from httpx import AsyncClient
import pytest

from backend.tests.utils import create_user_and_get_token, create_task


TEST_COMMENT_DATA = {"content": "test"}


@pytest.mark.anyio
async def test_create_comment(client: AsyncClient):
    user = await create_user_and_get_token(client)
    task = await create_task(client, headers=user["headers"])
    comment_data = TEST_COMMENT_DATA.copy()
    create_response = await client.post(
        f"/tasks/{task['id']}/comments", headers=user["headers"], json=comment_data
    )
    assert create_response.status_code == 200


@pytest.mark.anyio
async def test_success_get_comment(client: AsyncClient):
    user = await create_user_and_get_token(client)
    task = await create_task(client, headers=user["headers"])
    comment_data = TEST_COMMENT_DATA.copy()
    create_response = await client.post(
        f"/tasks/{task['id']}/comments", headers=user["headers"], json=comment_data
    )
    assert create_response.status_code == 200
    comment = create_response.json()

    get_response = await client.get(
        f"/tasks/{task['id']}/comments/{comment['id']}", headers=user["headers"]
    )
    assert get_response.status_code == 200


@pytest.mark.anyio
async def test_404_get_comment(client: AsyncClient):
    user = await create_user_and_get_token(client)
    task = await create_task(client, headers=user["headers"])
    get_response = await client.get(
        f"/tasks/{task['id']}/comments/1", headers=user["headers"]
    )
    assert get_response.status_code == 404


@pytest.mark.anyio
async def test_403_get_comment(client: AsyncClient):
    user = await create_user_and_get_token(client)
    user2 = await create_user_and_get_token(client)
    task = await create_task(client, headers=user2["headers"])
    comment_data = TEST_COMMENT_DATA.copy()
    create_response = await client.post(
        f"/tasks/{task['id']}/comments", headers=user2["headers"], json=comment_data
    )
    assert create_response.status_code == 200
    comment = create_response.json()

    get_response = await client.get(
        f"/tasks/{task['id']}/comments/{comment['id']}", headers=user["headers"]
    )
    assert get_response.status_code == 403


@pytest.mark.anyio
async def test_update_comment(client: AsyncClient):
    user = await create_user_and_get_token(client)
    task = await create_task(client, headers=user["headers"])
    comment_data = TEST_COMMENT_DATA.copy()
    create_response = await client.post(
        f"/tasks/{task['id']}/comments", headers=user["headers"], json=comment_data
    )
    assert create_response.status_code == 200
    comment = create_response.json()

    update_response = await client.put(
        f"/tasks/{task['id']}/comments/{comment['id']}",
        headers=user["headers"],
        json={"content": "changed"},
    )
    assert update_response.status_code == 200


@pytest.mark.anyio
async def test_403_update_comment(client: AsyncClient):
    user = await create_user_and_get_token(client)
    user2 = await create_user_and_get_token(client)
    task = await create_task(client, headers=user2["headers"])
    comment_data = TEST_COMMENT_DATA.copy()
    create_response = await client.post(
        f"/tasks/{task['id']}/comments", headers=user2["headers"], json=comment_data
    )
    assert create_response.status_code == 200
    comment = create_response.json()

    update_response = await client.put(
        f"/tasks/{task['id']}/comments/{comment['id']}",
        headers=user["headers"],
        json={"content": "changed"},
    )
    assert update_response.status_code == 403


@pytest.mark.anyio
async def test_delete_comment(client: AsyncClient):
    user = await create_user_and_get_token(client)
    task = await create_task(client, headers=user["headers"])
    comment_data = TEST_COMMENT_DATA.copy()
    create_response = await client.post(
        f"/tasks/{task['id']}/comments", headers=user["headers"], json=comment_data
    )
    assert create_response.status_code == 200
    comment = create_response.json()

    delete_response = await client.delete(
        f"/tasks/{task['id']}/comments/{comment['id']}", headers=user["headers"]
    )
    assert delete_response.status_code == 200


@pytest.mark.anyio
async def test_403_delete_comment(client: AsyncClient):
    user = await create_user_and_get_token(client)
    user2 = await create_user_and_get_token(client)
    task = await create_task(client, headers=user2["headers"])
    comment_data = TEST_COMMENT_DATA.copy()
    create_response = await client.post(
        f"/tasks/{task['id']}/comments", headers=user2["headers"], json=comment_data
    )
    assert create_response.status_code == 200
    comment = create_response.json()

    delete_response = await client.delete(
        f"/tasks/{task['id']}/comments/{comment['id']}", headers=user["headers"]
    )
    assert delete_response.status_code == 403


# @pytest.mark.anyio
# async def test_get_comments(client: AsyncClient):
#     user = await create_user_and_get_token(client)
#     task = await create_task(client)

#     create_response = await client.get
