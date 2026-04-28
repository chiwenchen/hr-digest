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
    mock_pdf_fetcher = AsyncMock()
    mock_pdf_fetcher.fetch_text.return_value = None
    builder = DigestBuilder(
        law_crawler=mock_law_crawler, news_crawler=mock_news_crawler,
        bill_crawler=mock_bill_crawler, summarizer=mock_summarizer, db=db,
        bill_pdf_fetcher=mock_pdf_fetcher,
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

    mock_pdf_fetcher = AsyncMock()
    mock_pdf_fetcher.fetch_text.return_value = "草案全文：規範製造者保存產銷資料 10 年"

    builder = DigestBuilder(
        law_crawler=mock_law_crawler, news_crawler=mock_news_crawler,
        bill_crawler=mock_bill_crawler, summarizer=mock_summarizer, db=db,
        bill_pdf_fetcher=mock_pdf_fetcher,
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

    # PDF fetched once for the new bill only (not for the upsert)
    mock_pdf_fetcher.fetch_text.assert_awaited_once_with("https://mol/B")

    # Summarizer called once with draft_text from PDF
    assert mock_summarizer.generate_bill_action_items.await_count == 1
    call_kwargs = mock_summarizer.generate_bill_action_items.await_args.kwargs
    assert call_kwargs["draft_text"] == "草案全文：規範製造者保存產銷資料 10 年"


@pytest.mark.asyncio
async def test_process_bills_persists_null_hr_preparation(db):
    """When summarizer returns hr_preparation=None (non-HR scope), the
    bill row must store NULL — not coerce to empty string."""
    mock_law_crawler = MagicMock()
    mock_law_crawler.fetch_all_laws = AsyncMock(return_value=[])
    mock_law_crawler.detect_changes.return_value = []
    mock_news_crawler = AsyncMock()
    mock_news_crawler.crawl.return_value = []
    mock_bill_crawler = AsyncMock()
    mock_bill_crawler.crawl.return_value = [
        RawBillItem(title="X 草案", url="https://mol/X", stage="預告中", published_date=date(2026, 5, 1)),
    ]
    mock_summarizer = AsyncMock()
    mock_summarizer.summarize_news.return_value = []
    mock_summarizer.generate_bill_action_items.return_value = {
        "impact_summary": "本草案主要規範製造者，非 HR 直接主責",
        "hr_preparation": None,
    }
    mock_pdf_fetcher = AsyncMock()
    mock_pdf_fetcher.fetch_text.return_value = None

    builder = DigestBuilder(
        law_crawler=mock_law_crawler, news_crawler=mock_news_crawler,
        bill_crawler=mock_bill_crawler, summarizer=mock_summarizer, db=db,
        bill_pdf_fetcher=mock_pdf_fetcher,
    )
    await builder.build(year=2026, month=5)

    result = await db.execute(select(Bill).where(Bill.source_url == "https://mol/X"))
    bill = result.scalar_one()
    assert bill.hr_preparation is None
    assert "非 HR 直接主責" in bill.impact_summary
