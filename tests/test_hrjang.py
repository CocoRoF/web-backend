"""
HRJang Router Tests
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_comments(client: AsyncClient):
    """Test get all comments."""
    response = await client.get("/api/v1/hrjang/comment/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
