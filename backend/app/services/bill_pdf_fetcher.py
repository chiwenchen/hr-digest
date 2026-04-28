from __future__ import annotations
import logging
import re
from io import BytesIO
from typing import Optional
import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader

logger = logging.getLogger(__name__)


class BillPdfFetcher:
    """Best-effort fetch of the full draft text PDF behind a MOL news URL.

    Resolves news.aspx → 行政院公報 detail → published PDF → text. Returns
    None for any failure (network, layout change, scanned PDF, parser error).
    Callers must treat None as 'no extra context, fall back to title-only'."""

    async def fetch_text(self, news_url: str) -> Optional[str]:
        try:
            async with httpx.AsyncClient(
                timeout=30, follow_redirects=True,
                headers={"User-Agent": "HRDigestBot/1.0"},
            ) as c:
                r = await c.get(news_url)
                r.raise_for_status()
                gazette_url = self._find_gazette_url(r.text)
                if not gazette_url:
                    logger.info("no gazette link on %s", news_url)
                    return None
                r = await c.get(gazette_url)
                r.raise_for_status()
                pdf_url = self._find_pdf_url(r.text)
                if not pdf_url:
                    logger.info("no PDF link on %s", gazette_url)
                    return None
                r = await c.get(pdf_url)
                r.raise_for_status()
                return self._extract_text(r.content)
        except Exception as e:
            logger.warning("Failed to fetch PDF text for %s: %s", news_url, e)
            return None

    @staticmethod
    def _find_gazette_url(html: str) -> Optional[str]:
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "gazette.nat.gov.tw" in href and "metaid" in href.lower():
                return href
        return None

    @staticmethod
    def _find_pdf_url(html: str) -> Optional[str]:
        soup = BeautifulSoup(html, "html.parser")
        candidates = [
            a["href"] for a in soup.find_all("a", href=True)
            if a["href"].lower().endswith(".pdf") and "gazette.nat.gov.tw" in a["href"]
        ]
        for url in candidates:
            if "Eg01" in url or "eg01" in url:
                return url
        return candidates[0] if candidates else None

    @staticmethod
    def _extract_text(pdf_bytes: bytes) -> Optional[str]:
        try:
            reader = PdfReader(BytesIO(pdf_bytes))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            text = re.sub(r"\s+", " ", text).strip()
            return text or None
        except Exception as e:
            logger.warning("Failed to extract PDF text: %s", e)
            return None
