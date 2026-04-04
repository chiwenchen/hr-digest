from __future__ import annotations
import logging
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.database import async_session
from app.services.law_crawler import LawCrawler
from app.services.news_crawler import NewsCrawler
from app.services.bill_crawler import BillCrawler
from app.services.summarizer import Summarizer
from app.services.digest_builder import DigestBuilder

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def run_monthly_digest():
    now = datetime.now(timezone.utc)
    async with async_session() as db:
        builder = DigestBuilder(
            law_crawler=LawCrawler(), news_crawler=NewsCrawler(),
            bill_crawler=BillCrawler(), summarizer=Summarizer(), db=db,
        )
        digest = await builder.build(year=now.year, month=now.month)
        logger.info("Monthly digest #%d created for %d-%02d", digest.id, now.year, now.month)

def start_scheduler():
    scheduler.add_job(run_monthly_digest, "cron", day=1, hour=8, minute=0, id="monthly_digest", replace_existing=True)
    scheduler.start()
    logger.info("Scheduler started — monthly digest job registered")
