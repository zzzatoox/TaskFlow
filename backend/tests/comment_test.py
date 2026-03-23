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


# @pytest.mark.anyio
# async def test_get_comments(client: AsyncClient):
#     user = await create_user_and_get_token(client)
#     task = await create_task(client)

#     create_response = await client.get
