import pytest
from unittest.mock import patch, MagicMock
from app.services.mailer import Mailer

def test_build_html_contains_all_blocks():
    mailer = Mailer()
    html = mailer.build_html(
        year=2026, month=4,
        law_changes=[{"article_number": "第24條", "law_name": "勞動基準法", "change_summary": "修訂摘要", "action_items": ["行動1"]}],
        calendar_items=[{"title": "勞退提繳率申報截止"}],
        news=[{"title": "新聞1", "source": "勞動部", "ai_summary": "摘要", "ai_action": "行動"}],
        bills=[{"title": "草案1", "status": "審查中", "impact_summary": "影響"}],
    )
    assert "第24條" in html
    assert "勞退提繳率申報截止" in html
    assert "新聞1" in html
    assert "草案1" in html
    assert "2026年4月" in html

@pytest.mark.asyncio
async def test_send_calls_resend():
    with patch("app.services.mailer.resend") as mock_resend:
        mock_resend.Emails.send.return_value = {"id": "test-id"}
        mailer = Mailer()
        result = await mailer.send(to=["hr@example.com"], subject="test", html="<h1>test</h1>")
    mock_resend.Emails.send.assert_called_once()
