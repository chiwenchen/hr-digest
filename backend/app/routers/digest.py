from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.db.models import Bill, Digest, HrCalendar, User
from app.auth.deps import get_current_user

router = APIRouter(prefix="/api/digest", tags=["digest"])


def serialize_digest(digest: Digest, calendar_items: list, bills: list) -> dict:
    return {
        "id": digest.id,
        "year": digest.year,
        "month": digest.month,
        "status": digest.status,
        "published_at": digest.published_at.isoformat() if digest.published_at else None,
        "law_changes": [
            {
                "id": lc.id,
                "law_name": lc.law_name,
                "article_number": lc.article_number,
                "change_summary": lc.change_summary,
                "action_items": lc.action_items,
            }
            for lc in digest.law_changes
        ],
        "news": [
            {
                "id": nc.id,
                "title": nc.title,
                "source": nc.source,
                "url": nc.url,
                "published_date": nc.published_date.isoformat() if nc.published_date else None,
                "ai_summary": nc.ai_summary,
                "ai_action": nc.ai_action,
                "sort_order": nc.sort_order,
            }
            for nc in sorted(
                [n for n in digest.news_candidates if n.is_approved],
                key=lambda n: (n.sort_order is None, n.sort_order),
            )
        ],
        "calendar": [
            {
                "id": c.id,
                "month": c.month,
                "quarter": c.quarter,
                "title": c.title,
                "description": c.description,
            }
            for c in calendar_items
        ],
        "bills": [
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
        ],
    }


async def _get_digest_with_context(digest: Digest, db: AsyncSession) -> dict:
    calendar_result = await db.execute(
        select(HrCalendar).where(
            (HrCalendar.month == digest.month) | (HrCalendar.month == 0)
        )
    )
    calendar_items = calendar_result.scalars().all()

    bills_result = await db.execute(select(Bill).where(Bill.is_active == True))
    bills = bills_result.scalars().all()

    return serialize_digest(digest, calendar_items, bills)


@router.get("/latest")
async def get_latest_digest(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Digest)
        .where(Digest.status == "published")
        .order_by(Digest.year.desc(), Digest.month.desc())
        .options(
            selectinload(Digest.law_changes),
            selectinload(Digest.news_candidates),
        )
        .limit(1)
    )
    digest = result.scalar_one_or_none()
    if not digest:
        raise HTTPException(status_code=404, detail="尚無已發佈的月刊")
    return await _get_digest_with_context(digest, db)


@router.get("/archive")
async def get_archive(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Digest)
        .where(Digest.status == "published")
        .order_by(Digest.year.desc(), Digest.month.desc())
    )
    digests = result.scalars().all()
    return [
        {
            "id": d.id,
            "year": d.year,
            "month": d.month,
            "published_at": d.published_at.isoformat() if d.published_at else None,
        }
        for d in digests
    ]


@router.get("/{digest_id}")
async def get_digest(
    digest_id: int,
    user: User = Depends(get_current_user),
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
        raise HTTPException(status_code=404, detail="找不到該月刊")
    return await _get_digest_with_context(digest, db)
