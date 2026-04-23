from __future__ import annotations
import json
import logging
import re
import anthropic
from app.config import settings

logger = logging.getLogger(__name__)


def _extract_json(text: str):
    """Parse JSON from Claude output, tolerating markdown fences and prose."""
    if not text:
        raise ValueError("empty response from model")
    # Strip ```json ... ``` fences
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback: find first {...} or [...] block
        match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        logger.error("Failed to parse JSON from model. Raw text: %r", text[:500])
        raise


class Summarizer:
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-sonnet-4-6"

    async def summarize_news(self, news_items: list[dict]) -> list[dict]:
        """Take raw news items and return top 10 with summary + HR action."""
        news_text = "\n".join(
            f"- 標題: {n['title']}, 來源: {n.get('source', '')}, URL: {n.get('url', '')}"
            for n in news_items
        )
        response = await self.client.messages.create(
            model=self.model, max_tokens=4096,
            messages=[{"role": "user", "content": f"""你是一位台灣 HR 法規專家。以下是本月蒐集到的 HR 相關新聞：

{news_text}

請從中選出最重要的 10 條新聞（依 HR 重要性排序），並為每條生成：
1. summary: 一段簡短中文摘要（50-100字）
2. action: 對 HR 人員的具體行動建議（30-80字）

回覆純 JSON 陣列格式，每個物件包含 title, summary, action 三個欄位。不要加入其他文字。"""}],
        )
        text = response.content[0].text
        return _extract_json(text)

    async def generate_law_action_items(self, law_name: str, article_number: str, content: str, previous_content: str = None) -> dict:
        """Generate HR action items for a law change."""
        diff_context = f"\n\n修改前條文：\n{previous_content}" if previous_content else ""
        response = await self.client.messages.create(
            model=self.model, max_tokens=2048,
            messages=[{"role": "user", "content": f"""你是一位台灣 HR 法規專家。以下法條已修訂，請分析對 HR 的影響：

法規：{law_name}
條號：{article_number}
修改後條文：
{content}{diff_context}

請回覆純 JSON 格式：
{{"summary": "修訂摘要（50-100字）", "action_items": ["HR 需要做的具體行動 1", "行動 2", ...]}}

不要加入其他文字。"""}],
        )
        text = response.content[0].text
        return _extract_json(text)
