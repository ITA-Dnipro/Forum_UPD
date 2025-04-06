import pytest
from httpx import AsyncClient, ASGITransport

from main import app

@pytest.mark.asyncio
async def test_get_startup_profiles():
    async with AsyncClient(transport=ASGITransport(app=app)) as ac:
        await ac.get()