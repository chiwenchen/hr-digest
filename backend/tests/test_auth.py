import pytest
import pytest_asyncio
import bcrypt as bcrypt_lib
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.models import User
from tests.conftest import test_session


@pytest_asyncio.fixture
async def seed_admin():
    async with test_session() as db:
        hashed = bcrypt_lib.hashpw("admin123".encode(), bcrypt_lib.gensalt()).decode()
        user = User(email="admin@example.com", hashed_password=hashed, name="Admin", role="admin")
        db.add(user)
        await db.commit()


@pytest.mark.asyncio
async def test_login_success(seed_admin):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/auth/login", json={"email": "admin@example.com", "password": "admin123"})
        assert resp.status_code == 200
        assert "access_token" in resp.cookies


@pytest.mark.asyncio
async def test_login_wrong_password(seed_admin):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/auth/login", json={"email": "admin@example.com", "password": "wrong"})
        assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_auth():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/auth/me")
        assert resp.status_code == 401
