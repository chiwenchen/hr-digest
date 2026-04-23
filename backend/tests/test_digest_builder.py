import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date
from sqlalchemy import select
from app.db.models import Digest, Bill
from app.services.digest_builder import DigestBuilder
from app.services.bill_crawler import RawBillItem


@pytest.mark.asyncio
async def test_build_monthly_digest_creates_draft(db):
    mock_law_crawler = MagicMock()
    mock_law_crawler.fetch_all_laws = AsyncMock(return_value=[])
    mock_law_crawler.detect_changes.return_value = []
    mock_news_crawler = AsyncMock()
    mock_news_crawler.crawl.return_value = [
        MagicMock(title="新聞1", source="勞動部", url="https://example.com/1", published_date=date(2026, 4, 1)),
    ]
    mock_summarizer = AsyncMock()
    mock_summarizer.summarize_news.return_value = [
        {"title": "新聞1", "summary": "摘要", "action": "行動建議"},
    ]
    mock_bill_crawler = AsyncMock()
    mock_bill_crawler.crawl.return_value = []
    builder = DigestBuilder(
        law_crawler=mock_law_crawler, news_crawler=mock_news_crawler,
        bill_crawler=mock_bill_crawler, summarizer=mock_summarizer, db=db,
    )
    digest = await builder.build(year=2026, month=4)
    assert digest.status == "draft"
    assert digest.year == 2026
    assert digest.month == 4


@pytest.mark.asyncio
async def test_process_bills_upserts_existing_and_inserts_new(db):
    """Crawler returns one already-tracked bill (new stage) and one new bill.
    Existing row's current_stage must update; new row must be inserted and
    enriched via summarizer.generate_bill_action_items."""
    existing = Bill(
        title="A 草案",
        source_url="https://mol/A",
        current_stage="委員會審查",
        is_active=True,
    )
    db.add(existing)
    await db.commit()

    mock_law_crawler = MagicMock()
    mock_law_crawler.fetch_all_laws = AsyncMock(return_value=[])
    mock_law_crawler.detect_changes.return_value = []

    mock_news_crawler = AsyncMock()
    mock_news_crawler.crawl.return_value = []

    mock_bill_crawler = AsyncMock()
    mock_bill_crawler.crawl.return_value = [
        RawBillItem(title="A 草案", url="https://mol/A", stage="二讀", published_date=date(2026, 5, 1)),
        RawBillItem(title="B 草案", url="https://mol/B", stage="委員會審查", published_date=date(2026, 5, 2)),
    ]

    mock_summarizer = AsyncMock()
    mock_summarizer.summarize_news.return_value = []
    mock_summarizer.generate_bill_action_items.return_value = {
        "impact_summary": "影響摘要",
        "hr_preparation": "HR 準備事項",
    }

    builder = DigestBuilder(
        law_crawler=mock_law_crawler, news_crawler=mock_news_crawler,
        bill_crawler=mock_bill_crawler, summarizer=mock_summarizer, db=db,
    )
    await builder.build(year=2026, month=5)

    result = await db.execute(select(Bill).order_by(Bill.source_url))
    bills = result.scalars().all()
    assert len(bills) == 2, "should be 2 bills (upsert + insert)"

    by_url = {b.source_url: b for b in bills}
    # Existing bill upserted: stage updated
    assert by_url["https://mol/A"].current_stage == "二讀"
    # New bill inserted with summarizer output
    assert by_url["https://mol/B"].impact_summary == "影響摘要"
    assert by_url["https://mol/B"].hr_preparation == "HR 準備事項"
    assert by_url["https://mol/B"].is_active is True

    # Summarizer called exactly once (for the new bill only, not the existing upsert)
    assert mock_summarizer.generate_bill_action_items.await_count == 1
