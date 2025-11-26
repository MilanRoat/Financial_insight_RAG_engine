# RAG Financial Analysis

## Overview
**RAG Financial Analysis** is a powerful tool designed to help investors make informed decisions by combining real-time financial data with AI-powered news analysis. The application fetches market data, scrapes the latest news articles, stores them in a vector database for semantic retrieval, and uses a Large Language Model (LLM) to generate comprehensive investment insights.(.env file is empty , use your own openai api key)

## Features
- **Real-Time Financial Data**: Fetches up-to-date stock information (Price, PE Ratio, Market Cap, EPS, etc.) using `yfinance`.
- **Intelligent News Scraping**: Automatically scrapes recent news headlines from **Finviz**, with a robust fallback to **Google News RSS** to ensure data availability.
- **RAG Pipeline (Retrieval-Augmented Generation)**:
    - **Vector Storage**: Embeds news articles using OpenAI's embedding models and stores them in **Qdrant** for efficient semantic search.
    - **Contextual Analysis**: Retrieves relevant news based on the stock ticker and uses **OpenAI (GPT-4o-mini)** to analyze the sentiment and impact on the company's financial health.
- **Modern Web UI**: A clean, responsive interface built with **FastAPI**, **Jinja2**, and **Tailwind CSS** (Dark Mode).
- **Containerized Deployment**: Fully dockerized services for easy setup and reproducibility.

## Tech Stack
- **Language**: Python 3.10+
- **Web Framework**: FastAPI
- **Database**: 
    - **PostgreSQL**: Stores structured company financial data and article metadata.
    - **Qdrant**: Stores vector embeddings for news articles.
- **AI/ML**: 
    - **OpenAI API**: For embeddings (`text-embedding-3-small`) and text generation (`gpt-4o-mini`).
- **Data Sources**: `yfinance`, `BeautifulSoup` (Web Scraping), `feedparser`.
- **Infrastructure**: Docker & Docker Compose.

## Project Structure
```
.
├── app/
│   ├── main.py          # FastAPI entry point
│   ├── database.py      # Database connections (Postgres & Qdrant)
│   ├── models.py        # SQLAlchemy models
│   ├── etl.py           # Data fetching and scraping logic
│   ├── rag.py           # Embedding, storage, and LLM analysis
│   └── templates/       # HTML templates
├── docker-compose.yml   # Service orchestration
├── Dockerfile           # Application container definition
├── requirements.txt     # Python dependencies
└── test_flow.py         # Standalone pipeline verification script
```

## Setup & Installation

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
- An [OpenAI API Key](https://platform.openai.com/).

### Installation
1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd antigravity-RAG
    ```

2.  **Configure Environment**:
    Create a `.env` file in the root directory (or update the existing one) with your OpenAI API key:
    ```env
    OPENAI_API_KEY=sk-your-api-key-here
    DATABASE_URL=postgresql://user:password@db:5432/rag_db
    QDRANT_URL=http://qdrant:6333
    ```

3.  **Run with Docker**:
    ```bash
    docker-compose up --build
    ```
    *Note: Ensure port `5432` is not occupied by a local PostgreSQL instance. If it is, stop the local service or modify the port mapping in `docker-compose.yml`.*

4.  **Access the Application**:
    Open your browser and navigate to: [http://localhost:8000](http://localhost:8000)

## Usage
1.  Enter a stock ticker symbol (e.g., `NVDA`, `AAPL`, `MSFT`) in the search bar.
2.  Click **Analyze**.
3.  Review the dashboard:
    - **Financial Stats**: Key market metrics.
    - **Recent News**: List of latest articles with links.
    - **AI Investment Analysis**: A generated report providing a "Buy", "Hold", or "Sell" recommendation based on the data.

## Troubleshooting
- **Port Conflicts**: If `docker-compose` fails with "Bind for 0.0.0.0:5432 failed", stop your local Postgres service:
    - Windows: `net stop postgresql-x64-15` (or similar service name)
    - Linux/Mac: `sudo service postgresql stop`
