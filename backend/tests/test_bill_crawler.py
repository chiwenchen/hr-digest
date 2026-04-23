from __future__ import annotations
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch
from datetime import date
from app.services.bill_crawler import BillCrawler, RawBillItem


FIXTURE_DIR = Path(__file__).parent / "fixtures"
MOL_DRAFTS_FIXTURE = (FIXTURE_DIR / "mol-drafts.html").read_text(encoding="utf-8")


def test_parse_mol_drafts_from_real_fixture():
    """Parser must handle the real laws.mol.gov.tw/drafts.aspx layout.

    Saved snapshot 2026-04-23 contains 10 draft rows. Verify the first row
    parses title (cleaned of 預告終止日 suffix), full URL, stage, and ROC
    date converted to Gregorian."""
    crawler = BillCrawler()
    items = crawler.parse_mol_draft_html(MOL_DRAFTS_FIXTURE)

    assert len(items) == 10

    first = items[0]
    assert first.title == "地方主管機關受理最高負責人職場霸凌事件申訴處理辦法草案"
    assert first.url == "https://laws.mol.gov.tw/news.aspx?msgid=6848&bak=0"
    assert first.stage == "預告中"
    assert first.published_date == date(2026, 4, 21)


def test_parse_skips_header_row():
    """Header row (公發布日 / 訊息摘要) must not become a draft item."""
    crawler = BillCrawler()
    items = crawler.parse_mol_draft_html(MOL_DRAFTS_FIXTURE)
    assert all("公發布日" not in it.title for it in items)
    assert all(it.url.startswith("https://laws.mol.gov.tw/") for it in items)


@pytest.mark.asyncio
async def test_crawl_returns_raw_items():
    crawler = BillCrawler()

    with patch.object(crawler, "_fetch_html", new=AsyncMock(return_value=MOL_DRAFTS_FIXTURE)):
        items = await crawler.crawl()

    assert isinstance(items, list)
    assert len(items) == 10
    assert all(isinstance(item, RawBillItem) for item in items)
    assert items[0].stage == "預告中"
