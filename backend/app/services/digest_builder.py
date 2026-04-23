from __future__ import annotations
import logging
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Digest, LawChange, NewsCandidate, Bill
from app.services.law_crawler import LawCrawler
from app.services.news_crawler import NewsCrawler
from app.services.bill_crawler import BillCrawler
from app.services.summarizer import Summarizer

logger = logging.getLogger(__name__)


class DigestBuilder:
    def __init__(self, law_crawler: LawCrawler, news_crawler: NewsCrawler, bill_crawler: BillCrawler, summarizer: Summarizer, db: AsyncSession):
        self.law_crawler = law_crawler
        self.news_crawler = news_crawler
        self.bill_crawler = bill_crawler
        self.summarizer = summarizer
        self.db = db

    async def build(self, year: int, month: int) -> Digest:
        digest = Digest(year=year, month=month, status="draft")
        self.db.add(digest)
        await self.db.flush()
        await self._process_law_changes(digest)
        await self._process_news(digest)
        await self._process_bills()
        await self.db.commit()
        await self.db.refresh(digest)
        logger.info("Built digest draft %d for %d-%02d", digest.id, year, month)
        return digest

    async def _process_law_changes(self, digest: Digest) -> None:
        current_articles = await self.law_crawler.fetch_all_laws()
        prev_result = await self.db.execute(
            select(LawChange).join(Digest).where(Digest.id != digest.id).order_by(Digest.created_at.desc())
        )
        previous_map = {lc.article_number: lc.change_summary for lc in prev_result.scalars().all()}
        changes = self.law_crawler.detect_changes(current_articles, previous_map)
        for change in changes:
            ai_result = await self.summarizer.generate_law_action_items(
                law_name=change["law_name"], article_number=change["article_number"],
                content=change["content"], previous_content=change.get("previous_content"),
            )
            law_change = LawChange(
                digest_id=digest.id, law_name=change["law_name"], article_number=change["article_number"],
                change_summary=ai_result["summary"], action_items=ai_result["action_items"],
            )
            self.db.add(law_change)

    async def _process_bills(self) -> None:
        """Crawl MOL draft bills and upsert into Bill table by source_url.

        Existing rows get current_stage + title refreshed. New rows get
        enriched with impact_summary + hr_preparation via the summarizer."""
        raw_items = await self.bill_crawler.crawl()
        if not raw_items:
            return
        urls = [item.url for item in raw_items]
        existing_result = await self.db.execute(select(Bill).where(Bill.source_url.in_(urls)))
        existing_by_url = {b.source_url: b for b in existing_result.scalars().all()}
        for item in raw_items:
            existing = existing_by_url.get(item.url)
            if existing:
                existing.current_stage = item.stage
                existing.title = item.title
                continue
            enrichment = await self.summarizer.generate_bill_action_items(
                title=item.title, source_url=item.url, stage=item.stage,
            )
            self.db.add(Bill(
                title=item.title,
                source_url=item.url,
                current_stage=item.stage,
                impact_summary=enrichment.get("impact_summary"),
                hr_preparation=enrichment.get("hr_preparation"),
                is_active=True,
            ))

    async def _process_news(self, digest: Digest) -> None:
        raw_items = await self.news_crawler.crawl()
        news_dicts = [{"title": item.title, "source": item.source, "url": item.url} for item in raw_items]
        summarized = await self.summarizer.summarize_news(news_dicts)
        for i, item in enumerate(summarized[:10]):
            matching_raw = next((r for r in raw_items if r.title == item.get("title")), None)
            news = NewsCandidate(
                digest_id=digest.id, title=item.get("title", ""),
                source=matching_raw.source if matching_raw else "",
                url=matching_raw.url if matching_raw else "",
                published_date=matching_raw.published_date or date.today() if matching_raw else date.today(),
                ai_summary=item.get("summary", ""), ai_action=item.get("action", ""),
                sort_order=i + 1,
            )
            self.db.add(news)
