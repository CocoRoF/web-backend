"""
HSKMap Router Tests
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_hskmap_without_data(client: AsyncClient):
    """Test HSK mapping endpoint (expects validation error without proper input)."""
    response = await client.post("/api/v1/hskmap/", json={})
    # Should return 422 for missing required fields
    assert response.status_code == 422
