from __future__ import annotations
import pytest
from unittest.mock import AsyncMock, patch
from datetime import date
from app.services.bill_crawler import BillCrawler, RawBillItem


SAMPLE_BILL_HTML = """
<html>
<body>
<table class="table">
  <thead>
    <tr><th>草案名稱</th><th>預告階段</th><th>公告日期</th></tr>
  </thead>
  <tbody>
    <tr>
      <td><a href="/1607/28162/28166/bill/001">勞動基準法第XX條修正草案</a></td>
      <td>預告中</td>
      <td>2024-03-20</td>
    </tr>
    <tr>
      <td><a href="/1607/28162/28166/bill/002">就業服務法部分條文修正草案</a></td>
      <td>已結束</td>
      <td>2024-02-28</td>
    </tr>
  </tbody>
</table>
</body>
</html>
"""


def test_parse_bill_html():
    crawler = BillCrawler()
    items = crawler.parse_mol_draft_html(SAMPLE_BILL_HTML)

    assert len(items) == 2
    assert items[0].title == "勞動基準法第XX條修正草案"
    assert items[0].url == "https://www.mol.gov.tw/1607/28162/28166/bill/001"
    assert items[0].stage == "預告中"
    assert items[0].published_date == date(2024, 3, 20)
    assert items[1].title == "就業服務法部分條文修正草案"
    assert items[1].stage == "已結束"
    assert items[1].published_date == date(2024, 2, 28)


@pytest.mark.asyncio
async def test_crawl_returns_raw_items():
    crawler = BillCrawler()

    with patch.object(crawler, "_fetch_html", new=AsyncMock(return_value=SAMPLE_BILL_HTML)):
        items = await crawler.crawl()

    assert isinstance(items, list)
    assert len(items) == 2
    assert all(isinstance(item, RawBillItem) for item in items)
    assert items[0].stage == "預告中"
