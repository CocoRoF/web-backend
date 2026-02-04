"""
Rara Router Tests
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_rara_surveys(client: AsyncClient):
    """Test get all surveys."""
    response = await client.get("/api/v1/rara/surveys/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
