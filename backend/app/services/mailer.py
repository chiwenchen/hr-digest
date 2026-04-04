from __future__ import annotations
import logging
import resend
from app.config import settings

logger = logging.getLogger(__name__)
resend.api_key = settings.resend_api_key

class Mailer:
    def build_html(self, year: int, month: int, law_changes: list[dict], calendar_items: list[dict], news: list[dict], bills: list[dict]) -> str:
        # Build law changes section
        if law_changes:
            law_items = ""
            for lc in law_changes:
                actions = "".join(f"<li>{a}</li>" for a in lc.get("action_items", []))
                law_items += f'<div style="margin-bottom:16px;"><strong>{lc["law_name"]} {lc["article_number"]}</strong><p>{lc["change_summary"]}</p><p>⚡ HR 需要做：</p><ul>{actions}</ul></div>'
            law_section = law_items
        else:
            law_section = "<p>本月無法條異動</p>"

        # Calendar section
        cal_items = "".join(f"<li>{c['title']}</li>" for c in calendar_items)
        cal_section = f"<ul>{cal_items}</ul>" if cal_items else "<p>本月無年曆提醒</p>"

        # News section
        news_items = ""
        for i, n in enumerate(news, 1):
            news_items += f'<div style="margin-bottom:12px;"><strong>{i}. {n["title"]}</strong> — {n.get("source", "")}<p>{n.get("ai_summary", "")}</p><p>💡 HR 注意：{n.get("ai_action", "")}</p></div>'

        # Bills section
        bill_items = ""
        for b in bills:
            bill_items += f'<div style="margin-bottom:12px;"><strong>🔍 {b["title"]}（{b.get("status", "")}）</strong><p>{b.get("impact_summary", "")}</p></div>'

        return f'''<html><body style="font-family:sans-serif;max-width:640px;margin:0 auto;padding:20px;">
            <h1 style="color:#1a1a2e;">{year}年{month}月 HR 行動月刊</h1>
            <h2>本月法條異動</h2>{law_section}<hr/>
            <h2>HR 年曆提醒</h2>{cal_section}<hr/>
            <h2>本月 HR 新聞</h2>{news_items}<hr/>
            <h2>法規雷達</h2>{bill_items if bill_items else "<p>目前無追蹤草案</p>"}<hr/>
            <p><a href="{settings.frontend_url}">查看完整版本 →</a></p>
        </body></html>'''

    async def send(self, to: list[str], subject: str, html: str) -> dict:
        result = resend.Emails.send({"from": settings.email_from, "to": to, "subject": subject, "html": html})
        logger.info("Email sent to %d recipients", len(to))
        return result
