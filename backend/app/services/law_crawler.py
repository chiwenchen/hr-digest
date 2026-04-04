from __future__ import annotations
import logging
from dataclasses import dataclass
import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://raw.githubusercontent.com/kong0107/mojLawSplitJSON/gh-pages/FalVMingLing"

HR_LAWS = {
    "N0030001": "勞動基準法",
    "N0030002": "勞工請假規則",
    "N0030003": "大量解僱勞工保護法",
    "N0030014": "勞資爭議處理法",
    "N0030015": "性別平等工作法",
    "N0050001": "勞工保險條例",
    "N0060001": "勞工退休金條例",
    "N0060002": "職業安全衛生法",
    "N0060003": "勞工職業災害保險及保護法",
    "N0090001": "就業保險法",
    "N0090003": "就業服務法",
}


@dataclass(frozen=True)
class LawArticleSnapshot:
    law_name: str
    article_number: str
    content: str


class LawCrawler:
    async def fetch_law_articles(self, law_id: str) -> list[LawArticleSnapshot]:
        url = f"{BASE_URL}/{law_id}.json"
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                logger.warning("Failed to fetch %s: %s", law_id, resp.status_code)
                return []
        data = resp.json()
        law_name = data.get("法規", {}).get("法規名稱", HR_LAWS.get(law_id, ""))
        articles_raw = data.get("法規", {}).get("法條", [])
        return [
            LawArticleSnapshot(
                law_name=law_name,
                article_number=a.get("條號", ""),
                content=a.get("條文內容", ""),
            )
            for a in articles_raw
        ]

    async def fetch_all_laws(self) -> list[LawArticleSnapshot]:
        all_articles = []
        for law_id in HR_LAWS:
            articles = await self.fetch_law_articles(law_id)
            all_articles.extend(articles)
        return all_articles

    def detect_changes(
        self, current: list[LawArticleSnapshot], previous: dict[str, str]
    ) -> list[dict]:
        changes = []
        for article in current:
            prev_content = previous.get(article.article_number)
            if prev_content is None:
                changes.append(
                    {
                        "type": "new",
                        "article_number": article.article_number,
                        "law_name": article.law_name,
                        "content": article.content,
                    }
                )
            elif prev_content != article.content:
                changes.append(
                    {
                        "type": "modified",
                        "article_number": article.article_number,
                        "law_name": article.law_name,
                        "content": article.content,
                        "previous_content": prev_content,
                    }
                )
        return changes
