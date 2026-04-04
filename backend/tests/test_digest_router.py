import pytest
import pytest_asyncio
import bcrypt as bcrypt_lib
from datetime import datetime, timezone, date
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.models import User, Digest, LawChange, NewsCandidate, HrCalendar
from tests.conftest import test_session


@pytest_asyncio.fixture
async def seed_user_and_digest():
    """Seed an HR user and a published digest with law change, news, and calendar."""
    async with test_session() as db:
        # Create HR user
        hashed = bcrypt_lib.hashpw("pass123".encode(), bcrypt_lib.gensalt()).decode()
        user = User(email="hr@example.com", hashed_password=hashed, name="HR User", role="hr")
        db.add(user)

        # Create published digest
        digest = Digest(year=2025, month=3, status="published", published_at=datetime.now(timezone.utc))
        db.add(digest)
        await db.flush()

        # Law change
        lc = LawChange(
            digest_id=digest.id,
            law_name="勞動基準法",
            article_number="第84條",
            change_summary="修正工時規定",
            action_items=["更新契約", "通知員工"],
        )
        db.add(lc)

        # Approved news
        news = NewsCandidate(
            digest_id=digest.id,
            title="最低工資調漲",
            source="勞動部",
            url="https://www.mol.gov.tw/news/1",
            published_date=date(2025, 3, 1),
            ai_summary="工資上調摘要",
            ai_action="更新薪資系統",
            sort_order=1,
            is_approved=True,
        )
        db.add(news)

        # Calendar item for month 3
        cal = HrCalendar(month=3, title="勞健保申報", description="每年三月申報")
        db.add(cal)

        # Every-month calendar item
        cal_every = HrCalendar(month=0, title="每月薪資處理", description="每月執行")
        db.add(cal_every)

        await db.commit()


@pytest.mark.asyncio
async def test_get_latest_digest(seed_user_and_digest):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Login first
        login_resp = await client.post("/api/auth/login", json={"email": "hr@example.com", "password": "pass123"})
        assert login_resp.status_code == 200

        resp = await client.get("/api/digest/latest", cookies=login_resp.cookies)
        assert resp.status_code == 200

        data = resp.json()
        assert data["year"] == 2025
        assert data["month"] == 3
        assert data["status"] == "published"
        assert "published_at" in data

        # law_changes populated
        assert len(data["law_changes"]) == 1
        assert data["law_changes"][0]["law_name"] == "勞動基準法"
        assert data["law_changes"][0]["action_items"] == ["更新契約", "通知員工"]

        # approved news
        assert len(data["news"]) == 1
        assert data["news"][0]["title"] == "最低工資調漲"

        # calendar: month 3 and month 0
        assert len(data["calendar"]) == 2
        calendar_titles = [c["title"] for c in data["calendar"]]
        assert "勞健保申報" in calendar_titles
        assert "每月薪資處理" in calendar_titles

        # bills key exists (empty since none seeded)
        assert "bills" in data


@pytest.mark.asyncio
async def test_get_latest_digest_requires_auth():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/digest/latest")
        assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_archive(seed_user_and_digest):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_resp = await client.post("/api/auth/login", json={"email": "hr@example.com", "password": "pass123"})
        resp = await client.get("/api/digest/archive", cookies=login_resp.cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        assert data[0]["year"] == 2025
        assert data[0]["month"] == 3
        assert "published_at" in data[0]
