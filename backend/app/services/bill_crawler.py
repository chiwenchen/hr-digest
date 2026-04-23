from __future__ import annotations
import logging
import re
from dataclasses import dataclass
from datetime import date
from typing import Optional
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

MOL_DRAFT_URL = "https://laws.mol.gov.tw/drafts.aspx?nh=n"
_MOL_DRAFT_BASE = "https://laws.mol.gov.tw/"
_TITLE_RE = re.compile(r"「(?P<name>[^」]+?)」(?P<suffix>[^（]*)")
_ROC_DATE_RE = re.compile(r"^\s*(\d{2,3})\.(\d{1,2})\.(\d{1,2})\s*$")


@dataclass(frozen=True)
class RawBillItem:
    title: str
    url: str
    stage: str
    published_date: Optional[date]


def _parse_roc_date(text: str) -> Optional[date]:
    """Convert ROC (民國) date like '115.04.21' to Gregorian date(2026, 4, 21)."""
    m = _ROC_DATE_RE.match(text)
    if not m:
        return None
    roc_year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
    try:
        return date(roc_year + 1911, month, day)
    except ValueError:
        return None


def _clean_title(raw: str) -> str:
    """Extract the draft name from '勞動部公告：預告「XXX」修正草案 （預告終止日：...）'.

    Falls back to the raw text stripped of the trailing parenthetical block."""
    m = _TITLE_RE.search(raw)
    if m:
        return f"{m.group('name')}{m.group('suffix').strip()}".strip()
    return re.sub(r"\s*（[^）]*）\s*$", "", raw).strip()


class BillCrawler:
    async def _fetch_html(self, url: str) -> str:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "HRDigestBot/1.0"})
            resp.raise_for_status()
            return resp.text

    def parse_mol_draft_html(self, html: str) -> list[RawBillItem]:
        soup = BeautifulSoup(html, "html.parser")
        table = soup.select_one("table.drafts-table") or soup.find("table")
        if table is None:
            return []
        items: list[RawBillItem] = []
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 2:
                continue
            pub_date = _parse_roc_date(cells[0].get_text(strip=True))
            a_tag = cells[1].find("a")
            if not a_tag:
                continue
            raw_title = a_tag.get_text(" ", strip=True)
            title = _clean_title(raw_title)
            href = a_tag.get("href", "")
            if href.startswith("http"):
                url = href
            elif href.startswith("/"):
                url = f"https://laws.mol.gov.tw{href}"
            else:
                url = f"{_MOL_DRAFT_BASE}{href}"
            items.append(
                RawBillItem(title=title, url=url, stage="預告中", published_date=pub_date)
            )
        return items

    async def crawl(self) -> list[RawBillItem]:
        all_items: list[RawBillItem] = []
        try:
            html = await self._fetch_html(MOL_DRAFT_URL)
            all_items.extend(self.parse_mol_draft_html(html))
        except Exception as e:
            logger.error("Failed to crawl MOL drafts: %s", e)
        return all_items
