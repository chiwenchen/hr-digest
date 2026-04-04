import pytest
import pytest_asyncio
import bcrypt as bcrypt_lib
from datetime import datetime, timezone, date
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.models import User, Digest, NewsCandidate, HrCalendar, Bill
from tests.conftest import test_session


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def admin_client():
    """Return an AsyncClient already logged-in as admin."""
    async with test_session() as db:
        hashed = bcrypt_lib.hashpw("admin123".encode(), bcrypt_lib.gensalt()).decode()
        user = User(email="admin@test.com", hashed_password=hashed, name="Admin", role="admin")
        db.add(user)
        await db.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_resp = await client.post("/api/auth/login", json={"email": "admin@test.com", "password": "admin123"})
        assert login_resp.status_code == 200
        client.cookies.update(login_resp.cookies)
        yield client


@pytest_asyncio.fixture
async def hr_client():
    """Return an AsyncClient logged-in as a non-admin HR user."""
    async with test_session() as db:
        hashed = bcrypt_lib.hashpw("hr123".encode(), bcrypt_lib.gensalt()).decode()
        user = User(email="hr@test.com", hashed_password=hashed, name="HR", role="hr")
        db.add(user)
        await db.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_resp = await client.post("/api/auth/login", json={"email": "hr@test.com", "password": "hr123"})
        assert login_resp.status_code == 200
        client.cookies.update(login_resp.cookies)
        yield client


@pytest_asyncio.fixture
async def seed_news(admin_client):
    """Seed a digest + unapproved news candidate."""
    async with test_session() as db:
        digest = Digest(year=2025, month=4, status="draft")
        db.add(digest)
        await db.flush()
        news = NewsCandidate(
            digest_id=digest.id,
            title="測試新聞",
            source="勞動部",
            url="https://example.com/news/1",
            published_date=date(2025, 4, 1),
            is_approved=False,
        )
        db.add(news)
        await db.commit()
        return news.id


@pytest_asyncio.fixture
async def seed_draft_digest():
    """Seed a draft digest for publish test."""
    async with test_session() as db:
        digest = Digest(year=2025, month=5, status="draft")
        db.add(digest)
        await db.commit()
        return digest.id


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_approve_news(admin_client, seed_news):
    news_id = seed_news
    resp = await admin_client.patch(f"/api/admin/news/{news_id}/approve")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == news_id
    assert data["is_approved"] is True


@pytest.mark.asyncio
async def test_create_calendar_item(admin_client):
    resp = await admin_client.post(
        "/api/admin/calendar",
        json={"month": 6, "title": "六月勞保申報", "description": "每年六月"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["month"] == 6
    assert data["title"] == "六月勞保申報"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_bill(admin_client):
    resp = await admin_client.post(
        "/api/admin/bills",
        json={
            "title": "勞動基準法修正草案",
            "status": "tracking",
            "impact_summary": "影響工時計算",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "勞動基準法修正草案"
    assert data["status"] == "tracking"
    assert data["is_active"] is True
    assert "id" in data


@pytest.mark.asyncio
async def test_publish_digest(admin_client, seed_draft_digest):
    digest_id = seed_draft_digest
    # Patch Mailer.send so no real email calls are made during test
    async def fake_send(self, to, subject, html):
        return {"id": "fake"}

    with patch("app.services.mailer.Mailer.send", new=fake_send):
        resp = await admin_client.post(f"/api/admin/digest/{digest_id}/publish")

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == digest_id
    assert data["status"] == "published"
    assert data["published_at"] is not None


@pytest.mark.asyncio
async def test_non_admin_rejected(hr_client, seed_news):
    """HR user should receive 403 on all admin endpoints."""
    news_id = seed_news

    resp = await hr_client.patch(f"/api/admin/news/{news_id}/approve")
    assert resp.status_code == 403

    resp = await hr_client.post("/api/admin/calendar", json={"month": 1, "title": "Test"})
    assert resp.status_code == 403

    resp = await hr_client.post("/api/admin/bills", json={"title": "Test Bill"})
    assert resp.status_code == 403

    resp = await hr_client.get("/api/admin/dashboard")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_list_calendar(admin_client):
    # Create one first
    await admin_client.post("/api/admin/calendar", json={"month": 2, "title": "二月薪資"})
    resp = await admin_client.get("/api/admin/calendar")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(c["title"] == "二月薪資" for c in data)


@pytest.mark.asyncio
async def test_delete_calendar_item(admin_client):
    create_resp = await admin_client.post("/api/admin/calendar", json={"month": 7, "title": "七月項目"})
    item_id = create_resp.json()["id"]

    resp = await admin_client.delete(f"/api/admin/calendar/{item_id}")
    assert resp.status_code == 204

    # Verify deleted
    list_resp = await admin_client.get("/api/admin/calendar")
    ids = [c["id"] for c in list_resp.json()]
    assert item_id not in ids


@pytest.mark.asyncio
async def test_dashboard(admin_client):
    resp = await admin_client.get("/api/admin/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert "pending_news_count" in data
    assert "latest_digest" in data
