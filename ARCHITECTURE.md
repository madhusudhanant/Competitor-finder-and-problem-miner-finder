# Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                 │
│  (Web Browser, cURL, Python requests, JavaScript fetch, etc.)       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ HTTP/REST API
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FASTAPI APPLICATION                            │
│                  (src/your_ai_service/api/main.py)                  │
│                                                                     │
│  • CORS Middleware                                                  │
│  • Request Validation (Pydantic)                                    │
│  • Route Management                                                 │
│  • Error Handling                                                   │
│  • API Documentation (Swagger/ReDoc)                                │
└────────────────────────────┬────────────────────────────────────────┘
                             │
            ┌────────────────┴──────────────── ┐
            │                                  │
            ▼                                  ▼
┌──────────────────────┐           ┌──────────────────────┐
│   API ENDPOINTS      │           │   API SCHEMAS        │
│   (v1/endpoints.py)  │           │   (v1/schemas.py)    │
│                      │           │                      │
│  • Health Check      │           │  • Request Models    │
│  • AI Extraction     │           │  • Response Models   │
│  • UGC Crawling      │           │  • Validation Rules  │
│  • Data Query        │           │  • Type Safety       │
│  • Export            │           └──────────────────────┘
└──────────┬───────────┘
           │
           │ Calls
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      COMPONENT LAYER                                 │
└─────────────────────────────────────────────────────────────────────┘
           │
    ┌──────┴──────┬──────────────┬─────────────┐
    │             │              │             │
    ▼             ▼              ▼             ▼
┌────────┐  ┌─────────┐  ┌──────────┐  ┌──────────┐
│   AI   │  │   UGC   │  │  Reddit  │  │ Twitter  │
│Service │  │ Crawler │  │ Crawler  │  │ Crawler  │
└────┬───┘  └────┬────┘  └─────┬────┘  └─────┬────┘
     │           │             │             │
     │           └─────────────┴─────────────┘
     │                         │
     ▼                         ▼
┌────────────────┐    ┌─────────────────┐
│  Google Gemini │    │  External APIs  │
│      API       │    │                 │
│                │    │  • Reddit API   │
│  • Problem     │    │  • Twitter API  │
│    Extraction  │    └─────────────────┘
│  • Sentiment   │
│  • Analysis    │
└────────────────┘
           │
           │ Results
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DATABASE LAYER                                  │
│                    (db/models.py, db/connection.py)                  │
│                                                                       │
│  • SQLAlchemy ORM                                                    │
│  • UGC Posts Storage                                                 │
│  • Crawl Sessions                                                    │
│  • Query Repository                                                  │
└─────────────────────────────────────────────────────────────────────┘
```

## Request Flow

### Flow 1: Simple Text Extraction

```
User Request
     │
     ▼
POST /api/v1/ai/extract-problems
     │
     ▼
endpoints.py::extract_problems()
     │
     ▼
ai_service.py::ProblemExtractor.extract_problems()
     │
     ▼
Google Gemini API
     │
     ▼
Parse JSON Response
     │
     ▼
Return to User
```

### Flow 2: UGC Crawl + Extract

```
User Request
     │
     ▼
POST /api/v1/ai/extract-from-ugc
     │
     ▼
endpoints.py::extract_from_ugc()
     │
     ├─────────────────┐
     ▼                 ▼
Reddit Crawler    Twitter Crawler
     │                 │
     ▼                 ▼
Reddit API        Twitter API
     │                 │
     └────────┬────────┘
              │
              ▼
     Combine Text Content
              │
              ▼
     ProblemExtractor.extract_problems()
              │
              ▼
     Google Gemini API
              │
              ▼
     Parse & Return Results
              │
              ▼
     Save to Database (optional)
              │
              ▼
     Return to User
```

## Component Details

### AI Service Component
```
ai_service.py
├── ProblemExtractor
│   ├── __init__()
│   ├── _setup_client()
│   ├── _create_prompt()
│   ├── _call_gemini()
│   ├── _parse_json_response()
│   ├── extract_problems()
│   ├── analyze_sentiment()
│   └── batch_extract_problems()
└── format_problems_output()
```

### UGC Crawler Component
```
ugc_crawler.py
├── UGCCrawler
│   ├── __init__()
│   ├── _initialize_crawlers()
│   ├── crawl_all_platforms()
│   ├── get_crawled_data()
│   ├── export_data()
│   └── get_crawl_stats()
├── reddit_crawler.py
│   └── RedditCrawler
│       ├── crawl_keyword()
│       └── crawl_subreddit()
└── twitter_crawler.py
    └── TwitterCrawler
        └── crawl_keyword()
```

## Data Flow

### Input Data Types
1. **Plain Text** → Direct to AI Service
2. **Keyword** → UGC Crawlers → Text → AI Service
3. **Multiple Texts** → Batch Processing → AI Service

### Output Data Types
1. **Problems List** (JSON)
   - problem_statement
   - category
   - severity
   - affected_feature
   - user_impact

2. **Summary** (JSON)
   - total_problems
   - most_common_category
   - overall_sentiment

3. **Crawled Data** (JSON/CSV)
   - Posts with metadata
   - Platform information
   - Timestamps

## Technology Stack

```
┌─────────────────────────────────────┐
│         Application Layer           │
│  • FastAPI (Web Framework)          │
│  • Pydantic (Validation)            │
│  • Uvicorn (ASGI Server)            │
└─────────────────────────────────────┘
           │
┌─────────────────────────────────────┐
│         Service Layer               │
│  • Google Gemini (AI)               │
│  • PRAW (Reddit)                    │
│  • Tweepy (Twitter)                 │
└─────────────────────────────────────┘
           │
┌─────────────────────────────────────┐
│         Data Layer                  │
│  • SQLAlchemy (ORM)                 │
│  • SQLite/PostgreSQL (DB)           │
└─────────────────────────────────────┘
           │
┌─────────────────────────────────────┐
│         Infrastructure              │
│  • Loguru (Logging)                 │
│  • Python-dotenv (Config)           │
│  • Requests (HTTP)                  │
└─────────────────────────────────────┘
```

## Configuration Management

```
.env File
    │
    ▼
Settings (Pydantic BaseSettings)
    │
    ├─► AI Service (Gemini API Key)
    ├─► Reddit Crawler (Client ID/Secret)
    ├─► Twitter Crawler (Bearer Token)
    ├─► Database (Connection URL)
    └─► API Server (Host/Port)
```

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│         Development                     │
│  python main.py                         │
│  • Auto-reload enabled                  │
│  • Debug logging                        │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         Production (Future)             │
│  • Docker Container                     │
│  • Nginx Reverse Proxy                  │
│  • PostgreSQL Database                  │
│  • Redis Cache                          │
│  • Load Balancer                        │
└─────────────────────────────────────────┘
```

## Security Layers

```
1. Environment Variables (.env)
   ↓
2. API Key Validation
   ↓
3. Request Validation (Pydantic)
   ↓
4. Rate Limiting (Future)
   ↓
5. Authentication (Future)
   ↓
6. CORS Policy
```

## Monitoring & Logging

```
┌─────────────────────────────────────────┐
│         Logging (Loguru)                │
│  • INFO: Normal operations              │
│  • WARNING: Recoverable issues          │
│  • ERROR: Failed operations             │
│  • DEBUG: Detailed debugging            │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         Health Checks                   │
│  • API Status                           │
│  • Database Connection                  │
│  • External API Availability            │
│  • Component Status                     │
└─────────────────────────────────────────┘
```

This modular architecture provides:
- ✅ Clear separation of concerns
- ✅ Easy testing and maintenance
- ✅ Scalable design
- ✅ Reusable components
- ✅ Production-ready structure
