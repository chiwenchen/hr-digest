import pytest
import pytest_asyncio
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import User, Digest, LawChange, NewsCandidate, HrCalendar, Bill


@pytest.mark.asyncio
async def test_create_user(db: AsyncSession):
    user = User(
        email="test@example.com",
        hashed_password="hashed_pw_123",
        name="Test User",
        role="hr",
        email_subscribed=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.role == "hr"
    assert user.email_subscribed is True


@pytest.mark.asyncio
async def test_create_digest_with_law_changes(db: AsyncSession):
    digest = Digest(year=2024, month=1, status="draft")
    db.add(digest)
    await db.commit()
    await db.refresh(digest)

    law_change = LawChange(
        digest_id=digest.id,
        law_name="勞動基準法",
        article_number="第84條",
        change_summary="修正工時規定",
        action_items=["更新內部政策", "通知員工"],
    )
    db.add(law_change)
    await db.commit()
    await db.refresh(law_change)

    assert digest.id is not None
    assert digest.year == 2024
    assert digest.month == 1
    assert digest.status == "draft"

    assert law_change.id is not None
    assert law_change.digest_id == digest.id
    assert law_change.law_name == "勞動基準法"
    assert law_change.article_number == "第84條"
    assert law_change.change_summary == "修正工時規定"
    assert law_change.action_items == ["更新內部政策", "通知員工"]


@pytest.mark.asyncio
async def test_create_news_candidate(db: AsyncSession):
    digest = Digest(year=2024, month=2, status="draft")
    db.add(digest)
    await db.commit()
    await db.refresh(digest)

    news = NewsCandidate(
        digest_id=digest.id,
        title="勞工保險費率調整",
        source="勞動部",
        url="https://example.com/news/1",
        published_date=date(2024, 2, 15),
        ai_summary="本文介紹勞保費率調整說明",
        ai_action="HR需於下月更新薪資計算",
        sort_order=1,
        is_approved=False,
    )
    db.add(news)
    await db.commit()
    await db.refresh(news)

    assert news.id is not None
    assert news.digest_id == digest.id
    assert news.title == "勞工保險費率調整"
    assert news.source == "勞動部"
    assert news.url == "https://example.com/news/1"
    assert news.published_date == date(2024, 2, 15)
    assert news.ai_summary == "本文介紹勞保費率調整說明"
    assert news.sort_order == 1
    assert news.is_approved is False


@pytest.mark.asyncio
async def test_create_hr_calendar(db: AsyncSession):
    entry = HrCalendar(
        month=3,
        quarter=1,
        title="勞健保申報截止日",
        description="每年3月底前完成申報",
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)

    assert entry.id is not None
    assert entry.month == 3
    assert entry.quarter == 1
    assert entry.title == "勞健保申報截止日"
    assert entry.description == "每年3月底前完成申報"


@pytest.mark.asyncio
async def test_create_bill(db: AsyncSession):
    bill = Bill(
        title="勞動基準法修正草案",
        status="tracking",
        source_url="https://lis.ly.gov.tw/bill/1",
        current_stage="委員會審查",
        expected_timeline="2024 Q2",
        impact_summary="可能影響加班費計算方式",
        hr_preparation="需評估現有加班費制度",
        is_active=True,
    )
    db.add(bill)
    await db.commit()
    await db.refresh(bill)

    assert bill.id is not None
    assert bill.title == "勞動基準法修正草案"
    assert bill.status == "tracking"
    assert bill.source_url == "https://lis.ly.gov.tw/bill/1"
    assert bill.current_stage == "委員會審查"
    assert bill.expected_timeline == "2024 Q2"
    assert bill.impact_summary == "可能影響加班費計算方式"
    assert bill.hr_preparation == "需評估現有加班費制度"
    assert bill.is_active is True
