# Syndra Demo Dashboard

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?style=flat-square&logo=streamlit)
![REST API](https://img.shields.io/badge/REST%20API-FastAPI-009688?style=flat-square&logo=fastapi)

## What is this?

This repository contains the **presentation layer** for Syndra. It is a "thin client" Streamlit application designed strictly to serve as a visual SDK and B2B sales dashboard. 

This repository **does not** contain the core ingestion engine, the NLP inference logic, or the vector database. It simply performs HTTP GET requests to the production Syndra API and visualizes the resulting JSON payloads.

## The Real Product

**Syndra** is an institutional-grade, self-hosted, API-first Financial NLP Data-as-a-Service platform. 

The core value proposition of Syndra lies in its backend infrastructure:
- **Fault-Tolerant Extraction:** Automated ingestion of unstructured financial news and RSS feeds.
- **Local NLP Enrichment:** Sentiment analysis powered by domain-specific models (`ProsusAI/finbert`) running on dedicated hardware.
- **Semantic Vector Search:** High-performance similarity search backed by Qdrant.
- **Immutable Data Contracts:** Strict Pydantic validation and idempotent processing.

Syndra does not sell a graphical interface. It sells clean, structured, low-latency financial intelligence delivered via a versioned REST API. This dashboard is merely one example of how a client might consume that data.

## Quickstart: The API Contract

To interface with the core Syndra Data Engine, you bypass this repository entirely and hit the REST API directly.

### via cURL
```bash
curl "https://api.syndradata.com/api/v1/sentiment/NVDA" \
  -H "X-API-Key: your_provisioned_api_key"
```

### via Python
```python
import requests

headers = {"X-API-Key": "your_provisioned_api_key"}
response = requests.get("https://api.syndradata.com/api/v1/sentiment/NVDA", headers=headers)

data = response.json()
print(f"Sentiment for NVDA: {data['aggregated_sentiment']} (Score: {data['average_score']})")
```

## Local Setup

If you wish to run this visual dashboard locally for testing or integration demonstrations:

1. Clone this repository:
```bash
git clone https://github.com/FranSMM/syndra-demo.git
cd syndra-demo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Streamlit application:
```bash
streamlit run syndra_demo_app.py
```

*Note: You must have a valid `SYNDRA_API_KEY` configured in your local environment or Streamlit secrets to retrieve live data.*
