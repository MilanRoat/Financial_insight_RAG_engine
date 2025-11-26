from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Date
from .database import Base
from datetime import datetime

class CompanyFinance(Base):
    __tablename__ = "company_finance"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True)
    name = Column(String)
    sector = Column(String)
    price = Column(Float)
    market_cap = Column(String)
    pe_ratio = Column(Float)
    eps = Column(Float)
    fifty_two_week_high = Column(Float)
    fifty_two_week_low = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)

class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    title = Column(String)
    link = Column(String)
    source = Column(String)
    published_date = Column(String) # Keeping as string for simplicity in parsing diverse formats
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
