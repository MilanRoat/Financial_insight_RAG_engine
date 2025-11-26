import os
from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from openai import OpenAI
from .database import qdrant_client

# Initialize OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

COLLECTION_NAME = "news_articles"

def ensure_collection():
    """Ensures the Qdrant collection exists."""
    try:
        qdrant_client.get_collection(COLLECTION_NAME)
    except Exception:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=qmodels.VectorParams(size=1536, distance=qmodels.Distance.COSINE),
        )

def get_embedding(text: str) -> List[float]:
    """Generates embedding for a given text using OpenAI."""
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def embed_and_store_news(articles: List[Dict]):
    """Embeds news articles and stores them in Qdrant."""
    ensure_collection()
    
    points = []
    for idx, article in enumerate(articles):
        # Create a unique ID based on link hash or simple index if batching
        # Using a simple hash of the link for ID generation to avoid duplicates in vector DB
        import hashlib
        point_id = hashlib.md5(article['link'].encode()).hexdigest()
        
        text_to_embed = f"{article['title']} - {article['summary']}"
        vector = get_embedding(text_to_embed)
        
        points.append(qmodels.PointStruct(
            id=point_id,
            vector=vector,
            payload=article
        ))
    
    if points:
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )

def retrieve_relevant_news(ticker: str, limit: int = 3) -> List[Dict]:
    """Retrieves relevant news for a ticker from Qdrant."""
    ensure_collection()
    
    # We search for the ticker itself to find relevant articles
    query_vector = get_embedding(f"News about {ticker} financial status and outlook")
    
    search_result = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit,
        query_filter=qmodels.Filter(
            must=[
                qmodels.FieldCondition(
                    key="ticker",
                    match=qmodels.MatchValue(value=ticker.upper())
                )
            ]
        )
    )
    
    return [hit.payload for hit in search_result]

def analyze_company(ticker: str, finance_data: Dict) -> str:
    """Generates an investment analysis using LLM."""
    
    # Retrieve news
    news_articles = retrieve_relevant_news(ticker)
    news_context = "\n".join([f"- {art['title']} ({art['published_date']}): {art['summary']}" for art in news_articles])
    
    prompt = f"""
    You are a financial analyst. Analyze the following company based on the provided financial data and recent news.
    
    Company: {finance_data['name']} ({finance_data['ticker']})
    
    Financial Data:
    - Price: {finance_data['price']}
    - Market Cap: {finance_data['market_cap']}
    - PE Ratio: {finance_data['pe_ratio']}
    - EPS: {finance_data['eps']}
    - 52 Week High: {finance_data['fifty_two_week_high']}
    - 52 Week Low: {finance_data['fifty_two_week_low']}
    
    Recent News:
    {news_context}
    
    Task:
    Provide a comprehensive investment analysis. Discuss the financial health based on the metrics and how the recent news might impact the stock. Conclude with a recommendation (Buy, Hold, or Sell) and the reasoning.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful financial assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content
