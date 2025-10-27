# Competitor Finder - UGC Problem Miner

AI-powered API for crawling user-generated content from social media platforms and extracting problems/pain points using Google Gemini.

## Features

- 🔍 **Multi-Platform Crawling**: Fetch posts from Reddit and Twitter
- 🤖 **AI-Powered Analysis**: Extract problems and pain points using Google Gemini
- 📊 **Data Management**: Store, query, and export crawled data
- 🚀 **RESTful API**: Well-documented FastAPI endpoints
- 📦 **Modular Architecture**: Clean separation of concerns

## Architecture

```
src/your_ai_service/
├── api/
│   ├── main.py              # FastAPI application
│   └── v1/
│       ├── endpoints.py     # API endpoints
│       └── schemas.py       # Request/response models
├── components/
│   ├── ai_service.py        # Google Gemini integration
│   ├── ugc_crawler.py       # Multi-platform crawler
│   ├── reddit_crawler.py    # Reddit-specific crawler
│   └── twitter_crawler.py   # Twitter-specific crawler
├── db/
│   ├── models.py            # Database models
│   ├── connection.py        # Database connection
│   └── repository.py        # Data access layer
└── config.py                # Configuration management
```

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd "Competitor Finder - 12O"
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
```bash
cp .env.example .env
```

Edit `.env` with your API credentials:
- **GEMINI_API_KEY**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Reddit API**: Get from [Reddit Apps](https://www.reddit.com/prefs/apps)
- **Twitter API**: Get from [Twitter Developer Portal](https://developer.twitter.com/)

## Usage

### Start the API Server

```bash
python main.py
```

The API will be available at:
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Base URL**: http://localhost:8000

## API Endpoints

### 🤖 AI Service Endpoints

#### 1. Extract Problems from Text
```http
POST /api/v1/ai/extract-problems
```

**Request Body:**
```json
{
  "text": "Your user reviews or feedback text here..."
}
```

**Response:**
```json
{
  "problems": [
    {
      "problem_statement": "Users find the interface confusing",
      "category": "UI/UX",
      "severity": "High",
      "affected_feature": "Navigation",
      "user_impact": "Difficulty finding key features"
    }
  ],
  "summary": {
    "total_problems": 5,
    "most_common_category": "UI/UX",
    "overall_sentiment": "Negative"
  }
}
```

#### 2. Extract Problems from UGC (Combined)
```http
POST /api/v1/ai/extract-from-ugc
```

**Request Body:**
```json
{
  "keyword": "Notion",
  "platform": "reddit",
  "limit": 50
}
```

**Response:**
```json
{
  "keyword": "Notion",
  "platform": "reddit",
  "total_posts_analyzed": 50,
  "problems": [...],
  "summary": {...},
  "crawled_at": "2025-10-23T10:00:00Z"
}
```

#### 3. Batch Extract Problems
```http
POST /api/v1/ai/batch-extract
```

**Request Body:**
```json
["text1", "text2", "text3"]
```

### 🔍 UGC Crawling Endpoints

#### 1. Crawl Multiple Platforms
```http
POST /api/v1/crawl
```

**Request Body:**
```json
{
  "keyword": "Notion",
  "platforms": ["reddit", "twitter"],
  "max_posts_per_platform": 50,
  "include_comments": false,
  "subreddits": ["productivity", "notion"],
  "days_back": 7
}
```

#### 2. Simple Single Platform Crawl
```http
POST /api/v1/crawl/simple
```

**Request Body:**
```json
{
  "keyword": "Slack",
  "platform": "reddit",
  "max_posts": 50
}
```

#### 3. Get Crawled Data
```http
GET /api/v1/data?keyword=Notion&platform=reddit&limit=100
```

#### 4. Export Data
```http
POST /api/v1/export
```

**Request Body:**
```json
{
  "keyword": "Notion",
  "platform": "reddit",
  "format": "json",
  "filename": "notion_posts.json"
}
```

#### 5. Get Statistics
```http
GET /api/v1/stats
```

### 🏥 Health Check
```http
GET /api/v1/health
```

## Example Usage

### Using cURL

**Extract problems from text:**
```bash
curl -X POST "http://localhost:8000/api/v1/ai/extract-problems" \
  -H "Content-Type: application/json" \
  -d '{"text": "The app crashes frequently and the UI is confusing"}'
```

**Crawl and extract in one call:**
```bash
curl -X POST "http://localhost:8000/api/v1/ai/extract-from-ugc" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "Notion", "platform": "reddit", "limit": 30}'
```

### Using Python

```python
import requests

# Extract problems from UGC
response = requests.post(
    "http://localhost:8000/api/v1/ai/extract-from-ugc",
    json={
        "keyword": "Notion",
        "platform": "reddit",
        "limit": 50
    }
)

result = response.json()
print(f"Found {len(result['problems'])} problems")
for problem in result['problems']:
    print(f"- {problem['problem_statement']} ({problem['severity']})")
```

### Using JavaScript

```javascript
const response = await fetch('http://localhost:8000/api/v1/ai/extract-problems', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'Your feedback text here...'
  })
});

const data = await response.json();
console.log(`Found ${data.problems.length} problems`);
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes (for AI features) |
| `GEMINI_MODEL` | Gemini model name | No (default: gemini-1.5-flash) |
| `REDDIT_CLIENT_ID` | Reddit app client ID | Yes (for Reddit) |
| `REDDIT_CLIENT_SECRET` | Reddit app secret | Yes (for Reddit) |
| `TWITTER_BEARER_TOKEN` | Twitter API bearer token | Yes (for Twitter) |
| `DATABASE_URL` | Database connection string | No (default: SQLite) |
| `API_HOST` | API server host | No (default: 0.0.0.0) |
| `API_PORT` | API server port | No (default: 8000) |
| `LOG_LEVEL` | Logging level | No (default: INFO) |

## Project Structure

### Components

- **`ai_service.py`**: Google Gemini integration for problem extraction
- **`ugc_crawler.py`**: Multi-platform crawler orchestrator
- **`reddit_crawler.py`**: Reddit-specific crawling logic
- **`twitter_crawler.py`**: Twitter-specific crawling logic

### API Layer

- **`endpoints.py`**: RESTful API endpoints
- **`schemas.py`**: Pydantic models for request/response validation
- **`main.py`**: FastAPI application setup

### Database

- **`models.py`**: SQLAlchemy ORM models
- **`connection.py`**: Database connection management
- **`repository.py`**: Data access patterns

## Development

### Running in Development Mode

```bash
python main.py
```

The server will auto-reload on code changes.

### Running with Uvicorn

```bash
uvicorn src.your_ai_service.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing Endpoints

Use the interactive API documentation at http://localhost:8000/docs to test endpoints directly in your browser.

## Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not configured"**
   - Ensure you've set `GEMINI_API_KEY` in your `.env` file
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

2. **"Reddit credentials not configured"**
   - Set `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` in `.env`
   - Create a Reddit app at https://www.reddit.com/prefs/apps

3. **"Twitter bearer token not configured"**
   - Set `TWITTER_BEARER_TOKEN` in `.env`
   - Get credentials from Twitter Developer Portal

4. **Import errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Ensure you're in the project root directory

## API Rate Limits

- **Google Gemini**: Subject to your API quota
- **Reddit**: ~60 requests per minute
- **Twitter**: Varies by tier (Essential, Elevated, etc.)

## License

[Your License Here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.
