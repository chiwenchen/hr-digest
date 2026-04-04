"""Seed initial admin user and HR calendar data.
Usage: docker compose exec backend python -m scripts.seed
"""
import asyncio
import bcrypt as bcrypt_lib
from sqlalchemy import select
from app.db.database import async_session, engine
from app.db.models import Base, User, HrCalendar

HR_CALENDAR_ITEMS = [
    (0, "每月 10 日前完成勞健保費用繳納"),
    (0, "每月薪資單核發與歸檔"),
    (1, "年度勞動條件自主檢查"),
    (2, "春節前確認加班費計算與排班合規"),
    (3, "申報前一年度職業災害統計"),
    (4, "勞退提繳率申報截止"),
    (5, "職業災害保險申報"),
    (5, "所得稅扣繳與員工報稅相關作業"),
    (6, "年中考核（若適用）"),
    (7, "基本工資調整施行日確認"),
    (8, "實習生/暑期工讀相關合規檢查"),
    (9, "年度教育訓練時數檢視"),
    (10, "勞退自提意願調查"),
    (11, "年度調薪規劃與預算編列"),
    (12, "年終獎金計算與發放準備"),
    (12, "次年度人力規劃與招募計畫"),
]


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as db:
        result = await db.execute(select(User).where(User.email == "admin@hrdigest.local"))
        if not result.scalar_one_or_none():
            hashed = bcrypt_lib.hashpw("admin123".encode(), bcrypt_lib.gensalt()).decode()
            db.add(User(email="admin@hrdigest.local", hashed_password=hashed, name="系統管理員", role="admin"))
            print("Created admin user: admin@hrdigest.local / admin123")
        existing = await db.execute(select(HrCalendar))
        if not existing.scalars().first():
            for month, title in HR_CALENDAR_ITEMS:
                db.add(HrCalendar(month=month, title=title))
            print(f"Seeded {len(HR_CALENDAR_ITEMS)} HR calendar items")
        await db.commit()
    print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(main())
