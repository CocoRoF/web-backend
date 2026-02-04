"""
Blog Router Tests
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_read_root(client: AsyncClient):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Welcome to FastAPI Backend"


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_get_blog_images(client: AsyncClient):
    """Test get all blog images."""
    response = await client.get("/api/v1/blog/image/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_blog_posts(client: AsyncClient):
    """Test get all blog posts."""
    response = await client.get("/api/v1/blog/post/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_markdown_files(client: AsyncClient):
    """Test get markdown files."""
    response = await client.get("/api/v1/blog/markdown/files/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
