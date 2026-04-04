from __future__ import annotations
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.law_crawler import LawCrawler, LawArticleSnapshot


SAMPLE_LAW_RESPONSE = {
    "法規": {
        "法規名稱": "勞動基準法",
        "法條": [
            {"條號": "第1條", "條文內容": "為規定勞動條件最低標準，保障勞工權益，加強勞雇關係，促進社會與經濟發展，特制定本法。"},
            {"條號": "第2條", "條文內容": "本法用辭定義如左。"},
        ],
    }
}


@pytest.mark.asyncio
async def test_fetch_law_articles_returns_list():
    crawler = LawCrawler()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = SAMPLE_LAW_RESPONSE

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch("app.services.law_crawler.httpx.AsyncClient", return_value=mock_client):
        articles = await crawler.fetch_law_articles("N0030001")

    assert isinstance(articles, list)
    assert len(articles) == 2
    assert articles[0].law_name == "勞動基準法"
    assert articles[0].article_number == "第1條"
    assert articles[1].article_number == "第2條"


def test_detect_changes_finds_new_article():
    crawler = LawCrawler()
    current = [
        LawArticleSnapshot(law_name="勞動基準法", article_number="第1條", content="內容A"),
    ]
    previous: dict[str, str] = {}

    changes = crawler.detect_changes(current, previous)

    assert len(changes) == 1
    assert changes[0]["type"] == "new"
    assert changes[0]["article_number"] == "第1條"
    assert changes[0]["law_name"] == "勞動基準法"
    assert changes[0]["content"] == "內容A"


def test_detect_changes_finds_modified_article():
    crawler = LawCrawler()
    current = [
        LawArticleSnapshot(law_name="勞動基準法", article_number="第1條", content="新內容"),
    ]
    previous = {"第1條": "舊內容"}

    changes = crawler.detect_changes(current, previous)

    assert len(changes) == 1
    assert changes[0]["type"] == "modified"
    assert changes[0]["article_number"] == "第1條"
    assert changes[0]["content"] == "新內容"
    assert changes[0]["previous_content"] == "舊內容"


def test_detect_changes_no_change():
    crawler = LawCrawler()
    current = [
        LawArticleSnapshot(law_name="勞動基準法", article_number="第1條", content="相同內容"),
    ]
    previous = {"第1條": "相同內容"}

    changes = crawler.detect_changes(current, previous)

    assert changes == []
