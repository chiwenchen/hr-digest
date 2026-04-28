from __future__ import annotations
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.bill_pdf_fetcher import BillPdfFetcher


FIXTURE_DIR = Path(__file__).parent / "fixtures"
MACHINE_PDF_BYTES = (FIXTURE_DIR / "machine-draft.pdf").read_bytes()


def test_find_gazette_url_picks_metaid_link():
    html = '''<html><body>
      <a href="/foo">other</a>
      <a href="https://gazette.nat.gov.tw/egFront/detail.do?metaid=164810&log=detailLog">行政院公報</a>
      <a href="https://join.gov.tw/policies/gazette/metaId/164810">眾開講</a>
    </body></html>'''
    assert BillPdfFetcher._find_gazette_url(html) == \
        "https://gazette.nat.gov.tw/egFront/detail.do?metaid=164810&log=detailLog"


def test_find_gazette_url_returns_none_when_absent():
    html = '<html><body><a href="https://example.com">x</a></body></html>'
    assert BillPdfFetcher._find_gazette_url(html) is None


def test_find_pdf_url_prefers_eg01_over_oo():
    """Gazette pages link both Eg01.pdf (body) and OO.pdf (comment form);
    we want the body."""
    html = '''<html><body>
      <a href="/attachments/abc/download/policy.pdf">policy</a>
      <a href="https://gazette.nat.gov.tw/EG/.../images/OO.pdf">意見表</a>
      <a href="https://gazette.nat.gov.tw/EG/.../images/Eg01.pdf">公報全文</a>
    </body></html>'''
    assert BillPdfFetcher._find_pdf_url(html) == \
        "https://gazette.nat.gov.tw/EG/.../images/Eg01.pdf"


def test_find_pdf_url_falls_back_to_first_gazette_pdf():
    html = '''<html><body>
      <a href="https://gazette.nat.gov.tw/EG/.../images/anything.pdf">somefile</a>
    </body></html>'''
    assert BillPdfFetcher._find_pdf_url(html) == \
        "https://gazette.nat.gov.tw/EG/.../images/anything.pdf"


def test_find_pdf_url_skips_non_gazette_attachments():
    html = '''<html><body>
      <a href="/attachments/abc/download/policy.pdf">policy</a>
    </body></html>'''
    assert BillPdfFetcher._find_pdf_url(html) is None


def test_extract_text_from_real_machine_pdf():
    """The real 機械設備器具監督管理辦法 draft PDF must yield text containing
    the title and one of the substantive 修正重點."""
    text = BillPdfFetcher._extract_text(MACHINE_PDF_BYTES)
    assert text is not None
    assert "機械設備器具監督管理辦法" in text
    # The draft introduces 產銷資料 retention rules
    assert "產銷" in text


def test_extract_text_returns_none_for_garbage():
    assert BillPdfFetcher._extract_text(b"not a pdf") is None


@pytest.mark.asyncio
async def test_fetch_text_returns_none_on_network_error():
    """All exceptions in the fetch chain must yield None — never raise.
    Callers depend on this contract to fall back to title-only summary."""
    fetcher = BillPdfFetcher()
    with patch("app.services.bill_pdf_fetcher.httpx.AsyncClient") as MockClient:
        instance = MagicMock()
        instance.__aenter__ = AsyncMock(side_effect=RuntimeError("boom"))
        MockClient.return_value = instance
        result = await fetcher.fetch_text("https://laws.mol.gov.tw/news.aspx?msgid=6840&bak=0")
    assert result is None
