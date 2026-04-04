from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

import bcrypt as bcrypt_lib
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.deps import require_admin
from app.db.database import get_db
from app.db.models import Bill, Digest, HrCalendar, NewsCandidate, User
from app.services.mailer import Mailer
from app.services.scheduler import run_monthly_digest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ── Pydantic schemas ─────────────────────────────────────────────────────────

class NewsOrderBody(BaseModel):
    sort_order: int


class CalendarCreate(BaseModel):
    month: int
    quarter: Optional[int] = None
    title: str
    description: Optional[str] = None


class CalendarUpdate(BaseModel):
    month: Optional[int] = None
    quarter: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None


class BillCreate(BaseModel):
    title: str
    status: Optional[str] = "tracking"
    source_url: Optional[str] = None
    current_stage: Optional[str] = None
    expected_timeline: Optional[str] = None
    impact_summary: Optional[str] = None
    hr_preparation: Optional[str] = None
    is_active: Optional[bool] = True


class BillUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    source_url: Optional[str] = None
    current_stage: Optional[str] = None
    expected_timeline: Optional[str] = None
    impact_summary: Optional[str] = None
    hr_preparation: Optional[str] = None
    is_active: Optional[bool] = None


class CreateUserBody(BaseModel):
    email: str
    password: str
    name: str
    role: Optional[str] = "hr"


# ── News endpoints ────────────────────────────────────────────────────────────

@router.patch("/news/{news_id}/approve")
async def approve_news(
    news_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(NewsCandidate).where(NewsCandidate.id == news_id))
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="新聞不存在")
    news.is_approved = True
    await db.commit()
    return {"id": news.id, "is_approved": news.is_approved}


@router.patch("/news/{news_id}/reject")
async def reject_news(
    news_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(NewsCandidate).where(NewsCandidate.id == news_id))
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="新聞不存在")
    news.is_approved = False
    await db.commit()
    return {"id": news.id, "is_approved": news.is_approved}


@router.patch("/news/{news_id}/order")
async def update_news_order(
    news_id: int,
    body: NewsOrderBody,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(NewsCandidate).where(NewsCandidate.id == news_id))
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="新聞不存在")
    news.sort_order = body.sort_order
    await db.commit()
    return {"id": news.id, "sort_order": news.sort_order}


# ── Calendar endpoints ────────────────────────────────────────────────────────

@router.get("/calendar")
async def list_calendar(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(HrCalendar).order_by(HrCalendar.month))
    items = result.scalars().all()
    return [
        {
            "id": c.id,
            "month": c.month,
            "quarter": c.quarter,
            "title": c.title,
            "description": c.description,
        }
        for c in items
    ]


@router.post("/calendar", status_code=201)
async def create_calendar(
    body: CalendarCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    item = HrCalendar(
        month=body.month,
        quarter=body.quarter,
        title=body.title,
        description=body.description,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return {"id": item.id, "month": item.month, "quarter": item.quarter, "title": item.title, "description": item.description}


@router.patch("/calendar/{item_id}")
async def update_calendar(
    item_id: int,
    body: CalendarUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(HrCalendar).where(HrCalendar.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="年曆項目不存在")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(item, field, value)
    await db.commit()
    return {"id": item.id, "month": item.month, "quarter": item.quarter, "title": item.title, "description": item.description}


@router.delete("/calendar/{item_id}", status_code=204)
async def delete_calendar(
    item_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(HrCalendar).where(HrCalendar.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="年曆項目不存在")
    await db.delete(item)
    await db.commit()
    return Response(status_code=204)


# ── Bill endpoints ────────────────────────────────────────────────────────────

@router.get("/bills")
async def list_bills(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Bill))
    bills = result.scalars().all()
    return [
        {
            "id": b.id,
            "title": b.title,
            "status": b.status,
            "source_url": b.source_url,
            "current_stage": b.current_stage,
            "expected_timeline": b.expected_timeline,
            "impact_summary": b.impact_summary,
            "hr_preparation": b.hr_preparation,
            "is_active": b.is_active,
        }
        for b in bills
    ]


@router.post("/bills", status_code=201)
async def create_bill(
    body: BillCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    bill = Bill(
        title=body.title,
        status=body.status or "tracking",
        source_url=body.source_url,
        current_stage=body.current_stage,
        expected_timeline=body.expected_timeline,
        impact_summary=body.impact_summary,
        hr_preparation=body.hr_preparation,
        is_active=body.is_active if body.is_active is not None else True,
    )
    db.add(bill)
    await db.commit()
    await db.refresh(bill)
    return {"id": bill.id, "title": bill.title, "status": bill.status, "is_active": bill.is_active}


@router.patch("/bills/{bill_id}")
async def update_bill(
    bill_id: int,
    body: BillUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Bill).where(Bill.id == bill_id))
    bill = result.scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=404, detail="草案不存在")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(bill, field, value)
    await db.commit()
    return {"id": bill.id, "title": bill.title, "status": bill.status, "is_active": bill.is_active}


# ── Subscriber / user endpoints ───────────────────────────────────────────────

@router.get("/subscribers")
async def list_subscribers(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "name": u.name,
            "role": u.role,
            "email_subscribed": u.email_subscribed,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


@router.post("/subscribers", status_code=201)
async def create_subscriber(
    body: CreateUserBody,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email 已存在")
    hashed = bcrypt_lib.hashpw(body.password.encode(), bcrypt_lib.gensalt()).decode()
    user = User(email=body.email, hashed_password=hashed, name=body.name, role=body.role or "hr")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "email": user.email, "name": user.name, "role": user.role}


# ── Digest publish endpoint ───────────────────────────────────────────────────

@router.post("/digest/{digest_id}/publish")
async def publish_digest(
    digest_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Digest)
        .where(Digest.id == digest_id)
        .options(
            selectinload(Digest.law_changes),
            selectinload(Digest.news_candidates),
        )
    )
    digest = result.scalar_one_or_none()
    if not digest:
        raise HTTPException(status_code=404, detail="月刊不存在")

    digest.status = "published"
    digest.published_at = datetime.now(timezone.utc)
    await db.commit()

    # Fetch subscribers and additional data for email
    subscribers_result = await db.execute(
        select(User).where(User.email_subscribed == True)
    )
    subscribers = subscribers_result.scalars().all()
    recipient_emails = [u.email for u in subscribers]

    from app.db.models import HrCalendar, Bill
    from sqlalchemy import or_

    calendar_result = await db.execute(
        select(HrCalendar).where(
            (HrCalendar.month == digest.month) | (HrCalendar.month == 0)
        )
    )
    calendar_items = calendar_result.scalars().all()

    bills_result = await db.execute(select(Bill).where(Bill.is_active == True))
    bills = bills_result.scalars().all()

    if recipient_emails:
        mailer = Mailer()
        law_dicts = [
            {
                "law_name": lc.law_name,
                "article_number": lc.article_number,
                "change_summary": lc.change_summary,
                "action_items": lc.action_items or [],
            }
            for lc in digest.law_changes
        ]
        calendar_dicts = [{"title": c.title} for c in calendar_items]
        approved_news = sorted(
            [n for n in digest.news_candidates if n.is_approved],
            key=lambda n: (n.sort_order is None, n.sort_order),
        )
        news_dicts = [
            {
                "title": n.title,
                "source": n.source,
                "ai_summary": n.ai_summary,
                "ai_action": n.ai_action,
            }
            for n in approved_news
        ]
        bill_dicts = [
            {
                "title": b.title,
                "status": b.status,
                "impact_summary": b.impact_summary,
            }
            for b in bills
        ]
        html = mailer.build_html(
            year=digest.year,
            month=digest.month,
            law_changes=law_dicts,
            calendar_items=calendar_dicts,
            news=news_dicts,
            bills=bill_dicts,
        )
        subject = f"{digest.year}年{digest.month}月 HR 行動月刊"
        asyncio.create_task(mailer.send(to=recipient_emails, subject=subject, html=html))

    return {"id": digest.id, "status": digest.status, "published_at": digest.published_at.isoformat()}


# ── Crawl trigger ─────────────────────────────────────────────────────────────

@router.post("/crawl")
async def trigger_crawl(
    background_tasks: BackgroundTasks,
    admin: User = Depends(require_admin),
):
    background_tasks.add_task(run_monthly_digest)
    return {"message": "爬蟲任務已排入背景執行"}


# ── Dashboard ─────────────────────────────────────────────────────────────────

@router.get("/dashboard")
async def dashboard(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    latest_result = await db.execute(
        select(Digest)
        .where(Digest.status == "published")
        .order_by(Digest.year.desc(), Digest.month.desc())
        .limit(1)
    )
    latest = latest_result.scalar_one_or_none()

    pending_count_result = await db.execute(
        select(func.count()).select_from(NewsCandidate).where(NewsCandidate.is_approved == False)
    )
    pending_news_count = pending_count_result.scalar_one()

    latest_info = None
    if latest:
        latest_info = {
            "id": latest.id,
            "year": latest.year,
            "month": latest.month,
            "published_at": latest.published_at.isoformat() if latest.published_at else None,
        }

    return {
        "latest_digest": latest_info,
        "pending_news_count": pending_news_count,
    }
