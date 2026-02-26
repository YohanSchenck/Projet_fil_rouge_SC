import pytest
import pytest_asyncio  # <-- Importe ceci
from app.main import app
from httpx import ASGITransport, AsyncClient


@pytest_asyncio.fixture # <-- Utilise pytest_asyncio ici
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
