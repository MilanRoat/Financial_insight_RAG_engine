import os
from app.database import SessionLocal
from app.etl import fetch_finance_data, fetch_news_data
from app.rag import embed_and_store_news, analyze_company

def test_pipeline(ticker="NVDA"):
    print(f"--- Testing Pipeline for {ticker} ---")
    
    db = SessionLocal()
    
    # 1. Test Finance Data Fetching
    print("\n1. Fetching Finance Data...")
    finance_data = fetch_finance_data(ticker, db)
    if finance_data:
        print(f"SUCCESS: Fetched data for {finance_data['name']}")
        print(f"Price: {finance_data['price']}")
    else:
        print("FAILURE: Could not fetch finance data")
        return

    # 2. Test News Fetching
    print("\n2. Fetching News Data...")
    articles = fetch_news_data(ticker, db)
    if articles:
        print(f"SUCCESS: Fetched {len(articles)} articles")
        print(f"Sample Title: {articles[0]['title']}")
    else:
        print("WARNING: No articles found (or scraping failed)")
    
    # 3. Test Embedding & Storage
    if articles:
        print("\n3. Embedding and Storing News...")
        try:
            embed_and_store_news(articles)
            print("SUCCESS: Articles embedded and stored in Qdrant")
        except Exception as e:
            print(f"FAILURE: Embedding/Storage failed: {e}")

    # 4. Test Analysis
    print("\n4. Generating Analysis...")
    try:
        analysis = analyze_company(ticker, finance_data)
        print("SUCCESS: Analysis Generated")
        print("-" * 20)
        print(analysis[:500] + "...")
        print("-" * 20)
    except Exception as e:
        print(f"FAILURE: Analysis generation failed: {e}")

if __name__ == "__main__":
    # Ensure env vars are loaded if running locally without docker
    from dotenv import load_dotenv
    load_dotenv()
    
    test_pipeline()
