from __future__ import annotations
import pytest
from unittest.mock import AsyncMock, patch
from datetime import date
from app.services.news_crawler import NewsCrawler, RawNewsItem


SAMPLE_MOL_HTML = """
<html>
<body>
<div class="item_list2">
  <a href="/1607/1632/news/12345">勞動部公告最新勞基法修正重點</a>
  <div>發布日期：2024-03-15</div>
</div>
<div class="item_list2">
  <a href="/1607/1632/news/12346">性別平等工作法修正草案說明</a>
  <div>發布日期：2024-03-10</div>
</div>
</body>
</html>
"""


def test_parse_mol_news():
    crawler = NewsCrawler()
    items = crawler.parse_mol_html(SAMPLE_MOL_HTML)

    assert len(items) == 2
    assert items[0].title == "勞動部公告最新勞基法修正重點"
    assert items[0].url == "https://www.mol.gov.tw/1607/1632/news/12345"
    assert items[0].source == "勞動部"
    assert items[0].published_date == date(2024, 3, 15)
    assert items[1].title == "性別平等工作法修正草案說明"
    assert items[1].published_date == date(2024, 3, 10)


@pytest.mark.asyncio
async def test_crawl_returns_raw_items():
    crawler = NewsCrawler()

    with patch.object(crawler, "_fetch_html", new=AsyncMock(return_value=SAMPLE_MOL_HTML)):
        items = await crawler.crawl()

    assert isinstance(items, list)
    assert len(items) == 2
    assert all(isinstance(item, RawNewsItem) for item in items)
    assert items[0].source == "勞動部"
