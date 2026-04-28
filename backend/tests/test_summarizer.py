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
async def test_generate_bill_action_items():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps({
        "impact_summary": "本草案提高加班費倍率，將增加人事成本",
        "hr_preparation": "盤點加班實績，評估成本衝擊並擬定回應",
    }))]
    with patch("app.services.summarizer.anthropic.AsyncAnthropic") as MockAnthropic:
        mock_client = AsyncMock()
        mock_client.messages.create.return_value = mock_response
        MockAnthropic.return_value = mock_client
        summarizer = Summarizer()
        result = await summarizer.generate_bill_action_items(
            title="勞基法部分條文修正草案",
            source_url="https://www.mol.gov.tw/1607/28162/28166/draft/123",
            stage="委員會審查",
        )
    assert "impact_summary" in result
    assert "hr_preparation" in result
    assert result["impact_summary"].startswith("本草案")


@pytest.mark.asyncio
async def test_generate_bill_action_items_includes_draft_text_in_prompt():
    """When draft_text is provided, it must reach the Claude prompt so the
    model can ground its summary in the actual law content instead of the
    title alone."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps({
        "impact_summary": "x", "hr_preparation": "y",
    }))]
    captured = {}
    async def fake_create(**kwargs):
        captured["messages"] = kwargs["messages"]
        return mock_response
    with patch("app.services.summarizer.anthropic.AsyncAnthropic") as MockAnthropic:
        mock_client = MagicMock()
        mock_client.messages.create = fake_create
        MockAnthropic.return_value = mock_client
        summarizer = Summarizer()
        await summarizer.generate_bill_action_items(
            title="X 草案", source_url="https://example.com", stage="預告中",
            draft_text="此草案規範製造者保存產銷資料 10 年",
        )
    user_text = captured["messages"][0]["content"]
    assert "保存產銷資料" in user_text
    assert "草案全文" in user_text


@pytest.mark.asyncio
async def test_generate_bill_action_items_allows_null_hr_preparation():
    """For non-HR-scope drafts the model is permitted to return
    hr_preparation=null. Summarizer must not coerce that to a string."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps({
        "impact_summary": "本草案主要規範製造者，非 HR 直接主責",
        "hr_preparation": None,
    }))]
    with patch("app.services.summarizer.anthropic.AsyncAnthropic") as MockAnthropic:
        mock_client = AsyncMock()
        mock_client.messages.create.return_value = mock_response
        MockAnthropic.return_value = mock_client
        summarizer = Summarizer()
        result = await summarizer.generate_bill_action_items(
            title="機械設備器具監督管理辦法部分條文修正草案",
            source_url="https://example.com", stage="預告中",
        )
    assert result["hr_preparation"] is None
    assert "非 HR 直接主責" in result["impact_summary"]


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
