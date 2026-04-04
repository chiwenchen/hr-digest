import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.summarizer import Summarizer


@pytest.mark.asyncio
async def test_summarize_news_returns_structured_list():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps([
        {"title": "勞動部修正勞基法施行細則", "summary": "勞動部公告修正...", "action": "HR 需確認加班費計算是否需更新"},
    ]))]
    with patch("app.services.summarizer.anthropic.AsyncAnthropic") as MockAnthropic:
        mock_client = AsyncMock()
        mock_client.messages.create.return_value = mock_response
        MockAnthropic.return_value = mock_client
        summarizer = Summarizer()
        result = await summarizer.summarize_news([
            {"title": "勞動部修正勞基法施行細則", "source": "勞動部", "url": "https://example.com"},
        ])
    assert len(result) == 1
    assert "summary" in result[0]
    assert "action" in result[0]


@pytest.mark.asyncio
async def test_generate_law_action_items():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps({
        "summary": "加班費計算基準調整", "action_items": ["更新加班費計算公式", "確認薪資系統"],
    }))]
    with patch("app.services.summarizer.anthropic.AsyncAnthropic") as MockAnthropic:
        mock_client = AsyncMock()
        mock_client.messages.create.return_value = mock_response
        MockAnthropic.return_value = mock_client
        summarizer = Summarizer()
        result = await summarizer.generate_law_action_items(
            law_name="勞動基準法", article_number="第24條", content="修改後條文...", previous_content="原始條文...",
        )
    assert "summary" in result
    assert len(result["action_items"]) == 2
