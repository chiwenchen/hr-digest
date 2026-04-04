import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date
from app.db.models import Digest
from app.services.digest_builder import DigestBuilder


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
    builder = DigestBuilder(
        law_crawler=mock_law_crawler, news_crawler=mock_news_crawler,
        bill_crawler=AsyncMock(), summarizer=mock_summarizer, db=db,
    )
    digest = await builder.build(year=2026, month=4)
    assert digest.status == "draft"
    assert digest.year == 2026
    assert digest.month == 4
