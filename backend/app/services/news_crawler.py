from __future__ import annotations
import logging
import re
from dataclasses import dataclass
from datetime import date
from typing import Optional
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
MOL_NEWS_URL = "https://www.mol.gov.tw/1607/1632/1633/lpsimplelist"
_DATE_RE = re.compile(r"發布日期[：:]\s*(\d{4}-\d{2}-\d{2})")


@dataclass(frozen=True)
class RawNewsItem:
    title: str
    url: str
    source: str
    published_date: Optional[date]


class NewsCrawler:
    async def _fetch_html(self, url: str) -> str:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "HRDigestBot/1.0"})
            resp.raise_for_status()
            return resp.text

    def parse_mol_html(self, html: str) -> list[RawNewsItem]:
        soup = BeautifulSoup(html, "html.parser")
        items = []
        for block in soup.select("div.item_list2"):
            a_tag = block.find("a")
            if not a_tag:
                continue
            title = a_tag.get_text(strip=True)
            href = a_tag.get("href", "")
            url = f"https://www.mol.gov.tw{href}" if href.startswith("/") else href
            pub_date = None
            m = _DATE_RE.search(block.get_text(" ", strip=True))
            if m:
                try:
                    pub_date = date.fromisoformat(m.group(1))
                except ValueError:
                    pass
            items.append(
                RawNewsItem(title=title, url=url, source="勞動部", published_date=pub_date)
            )
        return items

    async def crawl(self) -> list[RawNewsItem]:
        all_items: list[RawNewsItem] = []
        try:
            html = await self._fetch_html(MOL_NEWS_URL)
            all_items.extend(self.parse_mol_html(html))
        except Exception as e:
            logger.error("Failed to crawl MOL news: %s", e)
        return all_items
