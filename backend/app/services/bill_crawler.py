from __future__ import annotations
import logging
from dataclasses import dataclass
from datetime import date
from typing import Optional
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
MOL_DRAFT_URL = "https://www.mol.gov.tw/1607/28162/28166/"


@dataclass(frozen=True)
class RawBillItem:
    title: str
    url: str
    stage: str
    published_date: Optional[date]


class BillCrawler:
    async def _fetch_html(self, url: str) -> str:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "HRDigestBot/1.0"})
            resp.raise_for_status()
            return resp.text

    def parse_mol_draft_html(self, html: str) -> list[RawBillItem]:
        soup = BeautifulSoup(html, "html.parser")
        items = []
        for row in soup.select("table.table tr"):
            cells = row.find_all("td")
            if len(cells) < 3:
                continue
            a_tag = cells[0].find("a")
            if not a_tag:
                continue
            title = a_tag.get_text(strip=True)
            href = a_tag.get("href", "")
            url = f"https://www.mol.gov.tw{href}" if href.startswith("/") else href
            stage = cells[1].get_text(strip=True)
            pub_date = None
            try:
                pub_date = date.fromisoformat(cells[2].get_text(strip=True))
            except ValueError:
                pass
            items.append(
                RawBillItem(title=title, url=url, stage=stage, published_date=pub_date)
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
