from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from .etl import fetch_finance_data, fetch_news_data
from .rag import embed_and_store_news, analyze_company
import os

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Setup templates
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(request: Request, ticker: str = Form(...), db: Session = Depends(get_db)):
    ticker = ticker.upper()
    
    # 1. Fetch Finance Data
    finance_data = fetch_finance_data(ticker, db)
    if not finance_data:
        return templates.TemplateResponse("index.html", {"request": request, "error": f"Could not fetch data for {ticker}"})

    # 2. Fetch News Data
    articles = fetch_news_data(ticker, db)
    
    # 3. Embed and Store News
    if articles:
        embed_and_store_news(articles)
    
    # 4. Analyze
    analysis = analyze_company(ticker, finance_data)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "ticker": ticker,
        "finance_data": finance_data,
        "articles": articles,
        "analysis": analysis
    })
