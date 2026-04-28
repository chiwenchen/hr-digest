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

    async def generate_bill_action_items(
        self, title: str, source_url: str, stage: str, draft_text: str | None = None,
    ) -> dict:
        """Generate impact summary + HR preparation for a draft bill.

        When draft_text is provided (full PDF text from gazette), the model
        grounds its analysis in the actual content instead of guessing from
        the title. The prompt also allows the model to opt out by returning
        hr_preparation=null when the draft's regulated parties (e.g. product
        manufacturers, importers, certifying bodies, plant safety staff)
        are not HR's direct responsibility — preventing the hallucinated
        "HR should inventory machinery" failure mode."""
        if draft_text:
            context_block = f"\n\n草案全文（可能截斷）：\n{draft_text[:8000]}"
        else:
            context_block = "\n\n（未取得草案全文，僅依標題判斷，請避免過度推論）"
        prompt = (
            "你是一位台灣 HR 法規專家。以下是勞動部預告的法規草案，請分析對 HR 的可能影響：\n\n"
            f"草案名稱：{title}\n"
            f"目前階段：{stage}\n"
            f"來源：{source_url}{context_block}\n\n"
            "判斷規則：\n"
            "1. 先判斷草案的真正規範對象。若主要對象為產品製造商、進口商、檢定機構、廠務或工安人員等\n"
            "   非 HR 直接主責角色，請於 impact_summary 開頭明確寫「本草案主要規範 X，非 HR 直接主責」\n"
            "   並說明真正的規範對象，並將 hr_preparation 設為 null。\n"
            "2. 若草案確實影響 HR（例如勞動條件、薪資、工時、勞工權益、員工教育訓練、職場心理健康等），\n"
            "   才在 hr_preparation 填入具體可執行事項。\n"
            "3. 嚴禁基於關鍵字聯想（例如看到「機械」就說 HR 要安排操作訓練）硬編內容。\n\n"
            "請回覆純 JSON 格式：\n"
            "{\"impact_summary\": \"80-120 字\", \"hr_preparation\": \"50-100 字 或 null\"}\n\n"
            "不要加入其他文字。"
        )
        response = await self.client.messages.create(
            model=self.model, max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
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
