import yfinance as yf
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .models import CompanyFinance, NewsArticle
from .database import SessionLocal
import feedparser
from datetime import datetime

def get_db_session():
    return SessionLocal()

def fetch_finance_data(ticker: str, db: Session):
    """Fetches financial data from yfinance and updates the database."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Extract relevant data
        finance_data = {
            "ticker": ticker.upper(),
            "name": info.get("longName", "N/A"),
            "sector": info.get("sector", "N/A"),
            "price": info.get("currentPrice", 0.0),
            "market_cap": str(info.get("marketCap", "N/A")),
            "pe_ratio": info.get("trailingPE", 0.0),
            "eps": info.get("trailingEps", 0.0),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh", 0.0),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow", 0.0),
            "last_updated": datetime.utcnow()
        }

        # Check if exists
        existing_company = db.query(CompanyFinance).filter(CompanyFinance.ticker == ticker.upper()).first()
        if existing_company:
            for key, value in finance_data.items():
                setattr(existing_company, key, value)
        else:
            new_company = CompanyFinance(**finance_data)
            db.add(new_company)
        
        db.commit()
        return finance_data
    except Exception as e:
        print(f"Error fetching finance data for {ticker}: {e}")
        return None

def scrape_finviz(ticker: str):
    """Scrapes news from Finviz."""
    url = f"https://finviz.com/quote.ashx?t={ticker}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        news_table = soup.find(id='news-table')
        
        articles = []
        if news_table:
            rows = news_table.findAll('tr')
            for row in rows:
                a_tag = row.find('a')
                if a_tag:
                    title = a_tag.text
                    link = a_tag['href']
                    source = "Finviz"
                    # Date parsing is tricky on finviz, skipping precise date for simplicity or using current time if not easily parsable
                    # Finviz format: "Nov-21-23 09:00PM" or "08:00PM"
                    date_data = row.td.text.strip()
                    
                    articles.append({
                        "ticker": ticker.upper(),
                        "title": title,
                        "link": link,
                        "source": source,
                        "published_date": date_data,
                        "summary": title # Using title as summary for now
                    })
                    if len(articles) >= 5: # Limit to 5 recent articles
                        break
        return articles
    except Exception as e:
        print(f"Error scraping Finviz for {ticker}: {e}")
        return []

def scrape_google_news(ticker: str):
    """Fallback: Scrapes Google News RSS."""
    rss_url = f"https://news.google.com/rss/search?q={ticker}"
    try:
        feed = feedparser.parse(rss_url)
        articles = []
        for entry in feed.entries[:5]:
            articles.append({
                "ticker": ticker.upper(),
                "title": entry.title,
                "link": entry.link,
                "source": "Google News",
                "published_date": entry.published,
                "summary": entry.summary if 'summary' in entry else entry.title
            })
        return articles
    except Exception as e:
        print(f"Error scraping Google News for {ticker}: {e}")
        return []

def fetch_news_data(ticker: str, db: Session):
    """Fetches news data from Finviz, falls back to Google News."""
    articles = scrape_finviz(ticker)
    
    if not articles:
        print(f"Finviz returned 0 articles for {ticker}. Switching to Google News fallback.")
        articles = scrape_google_news(ticker)
    
    # Store in DB
    stored_articles = []
    for art in articles:
        # Check duplicates by link
        exists = db.query(NewsArticle).filter(NewsArticle.link == art['link']).first()
        if not exists:
            new_article = NewsArticle(**art)
            db.add(new_article)
            stored_articles.append(art)
    
    db.commit()
    return stored_articles
