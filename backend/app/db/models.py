from __future__ import annotations
from datetime import datetime, date
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default="hr")  # "hr" | "admin"
    email_subscribed = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class Digest(Base):
    __tablename__ = "digests"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="draft")  # "draft" | "published"
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    law_changes = relationship("LawChange", back_populates="digest", cascade="all, delete-orphan")
    news_candidates = relationship("NewsCandidate", back_populates="digest", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("year", "month", name="uq_digest_year_month"),)


class LawChange(Base):
    __tablename__ = "law_changes"

    id = Column(Integer, primary_key=True)
    digest_id = Column(Integer, ForeignKey("digests.id"), nullable=False)
    law_name = Column(String(100), nullable=False)
    article_number = Column(String(20), nullable=False)
    change_summary = Column(Text, nullable=False)
    action_items = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, server_default=func.now())

    digest = relationship("Digest", back_populates="law_changes")


class NewsCandidate(Base):
    __tablename__ = "news_candidates"

    id = Column(Integer, primary_key=True)
    digest_id = Column(Integer, ForeignKey("digests.id"), nullable=False)
    title = Column(String(500), nullable=False)
    source = Column(String(100), nullable=False)
    url = Column(String(1000), nullable=False)
    published_date = Column(Date, nullable=False)
    ai_summary = Column(Text, nullable=True)
    ai_action = Column(Text, nullable=True)
    sort_order = Column(Integer, nullable=True)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    digest = relationship("Digest", back_populates="news_candidates")


class HrCalendar(Base):
    __tablename__ = "hr_calendar"

    id = Column(Integer, primary_key=True)
    month = Column(Integer, nullable=False)  # 1-12; 0 = every month
    quarter = Column(Integer, nullable=True)  # 1-4; NULL = not quarterly
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    status = Column(String(50), nullable=False, default="tracking")
    source_url = Column(String(1000), nullable=True)
    current_stage = Column(String(200), nullable=True)
    expected_timeline = Column(String(200), nullable=True)
    impact_summary = Column(Text, nullable=True)
    hr_preparation = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())
