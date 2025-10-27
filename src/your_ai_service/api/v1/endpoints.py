"""
API endpoints for UGC crawler service.
"""
import os
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from loguru import logger

from ...components.ugc_crawler import UGCCrawler
from ...components.ai_service import ProblemExtractor
from ...db.connection import get_db
from ...config import settings
from .schemas import (
    CrawlRequest, SimpleCrawlRequest, CrawlResponse,
    DataQueryRequest, DataQueryResponse, UGCPostResponse,
    ExportRequest, ExportResponse,
    StatsResponse, HealthResponse,
    ExtractProblemsRequest, ExtractProblemsResponse,
    ExtractFromUGCRequest, ExtractFromUGCResponse,
    MineProblemsRequest, MineProblemsResponse
)

router = APIRouter()

# Global UGC crawler instance
ugc_crawler = UGCCrawler()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check database connection
        db_connected = False
        try:
            from ...db.connection import db_manager
            session = db_manager.get_session()
            session.execute("SELECT 1")
            session.close()
            db_connected = True
        except Exception:
            pass
        
        # Check crawler availability
        reddit_available = ugc_crawler.reddit_crawler is not None
        twitter_available = ugc_crawler.twitter_crawler is not None
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow().isoformat(),
            version="1.0.0",
            database_connected=db_connected,
            reddit_available=reddit_available,
            twitter_available=twitter_available
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crawl", response_model=CrawlResponse)
async def crawl_platforms(
    request: CrawlRequest,
    background_tasks: BackgroundTasks
):
    """
    Crawl multiple platforms for a given keyword.
    This endpoint starts the crawling process in the background.
    """
    try:
        # Validate platforms
        supported_platforms = ["reddit", "twitter"]
        invalid_platforms = [p for p in request.platforms if p not in supported_platforms]
        if invalid_platforms:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported platforms: {invalid_platforms}. Supported: {supported_platforms}"
            )
        
        # Start crawling in background
        result = ugc_crawler.crawl_all_platforms(
            keyword=request.keyword,
            platforms=request.platforms,
            max_posts_per_platform=request.max_posts_per_platform,
            include_comments=request.include_comments,
            subreddits=request.subreddits,
            days_back=request.days_back
        )
        
        # Calculate total collected posts
        total_collected = 0
        for platform_data in result.values():
            if isinstance(platform_data, dict) and "total_posts" in platform_data:
                total_collected += platform_data.get("total_posts", 0)
        
        # Format response to match CrawlResponse schema
        response = CrawlResponse(
            session_id=0,  # You can generate a unique ID if needed
            keyword=request.keyword,
            status="completed",
            total_collected=total_collected,
            platforms=result,
            started_at=datetime.utcnow().isoformat() + "Z",
            completed_at=datetime.utcnow().isoformat() + "Z",
            error=None
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Crawl request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crawl/simple", response_model=CrawlResponse)
async def crawl_simple(request: SimpleCrawlRequest):
    """
    Simple crawl endpoint for a single platform.
    Suitable for testing and small-scale crawling.
    """
    try:
        if request.platform not in ["reddit", "twitter"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported platform: {request.platform}. Use 'reddit' or 'twitter'"
            )
        
        result = ugc_crawler.crawl_keyword_simple(
            keyword=request.keyword,
            platform=request.platform,
            max_posts=request.max_posts
        )
        
        # Convert to response format matching CrawlResponse schema
        response_data = {
            "session_id": 0,
            "keyword": result.get("keyword", request.keyword),
            "status": "completed",
            "total_collected": result.get("total_posts", 0),
            "platforms": {request.platform: result},
            "started_at": result.get("timestamp", datetime.utcnow().isoformat() + "Z"),
            "completed_at": datetime.utcnow().isoformat() + "Z",
            "error": None
        }
        
        return CrawlResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Simple crawl failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data", response_model=DataQueryResponse)
async def get_crawled_data(
    keyword: Optional[str] = Query(None, description="Filter by keyword"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get crawled data with optional filters."""
    try:
        # Parse dates
        start_dt = None
        end_dt = None
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        # Get data
        posts_data = ugc_crawler.get_crawled_data(
            keyword=keyword,
            platform=platform,
            limit=limit,
            start_date=start_dt,
            end_date=end_dt
        )
        
        # Convert to response models
        posts = [UGCPostResponse(**post) for post in posts_data]
        
        return DataQueryResponse(
            total_count=len(posts),
            posts=posts,
            filters_applied={
                "keyword": keyword,
                "platform": platform,
                "limit": limit,
                "start_date": start_date,
                "end_date": end_date
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Data query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export", response_model=ExportResponse)
async def export_data(request: ExportRequest):
    """Export crawled data to file."""
    try:
        if request.format not in ["json", "csv"]:
            raise HTTPException(
                status_code=400,
                detail="Unsupported format. Use 'json' or 'csv'"
            )
        
        filepath = ugc_crawler.export_data(
            keyword=request.keyword,
            platform=request.platform,
            format=request.format,
            filename=request.filename
        )
        
        if not filepath:
            raise HTTPException(status_code=404, detail="No data found to export")
        
        # Get file info
        file_size = os.path.getsize(filepath)
        record_count = 0
        
        # Count records for response
        data = ugc_crawler.get_crawled_data(
            keyword=request.keyword,
            platform=request.platform
        )
        record_count = len(data)
        
        return ExportResponse(
            filename=os.path.basename(filepath),
            filepath=filepath,
            record_count=record_count,
            format=request.format,
            created_at=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/download/{filename:path}")
async def download_export(filename: str):
    """Download an exported data file."""
    try:
        # Support both base filename and path-like values (e.g., data/exports/file.json)
        base_dir = settings.data_dir
        has_sep = ('/' in filename) or ('\\' in filename)
        # Build candidate paths conservatively to avoid duplicating segments
        candidates = []
        if has_sep:
            # If user passed a relative path like "exports/x.json" or "data/exports/x.json"
            candidates.append(os.path.join(base_dir, filename))
            # Also consider the raw value (in case an absolute path was provided)
            candidates.append(filename)
        else:
            # Plain filename: try exports subdir first, then root data dir
            candidates.append(os.path.join(base_dir, 'exports', filename))
            candidates.append(os.path.join(base_dir, filename))
            # As a fallback, current working directory
            candidates.append(filename)
        filepath = next((p for p in candidates if os.path.exists(p)), None)

        if not filepath:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Determine media type
        media_type = "application/json" if filename.endswith('.json') else "text/csv"
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type=media_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get crawling statistics."""
    try:
        stats = ugc_crawler.get_crawl_stats()
        return StatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Stats request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/data")
async def clear_data(
    keyword: Optional[str] = Query(None, description="Clear data for specific keyword"),
    platform: Optional[str] = Query(None, description="Clear data for specific platform"),
    confirm: bool = Query(False, description="Confirmation flag")
):
    """Clear crawled data (with confirmation)."""
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Set confirm=true to proceed with data deletion"
        )
    
    try:
        # Use UGCCrawler method for consistency
        result = ugc_crawler.delete_data(
            keyword=keyword,
            platform=platform
        )
        
        return {
            "message": result.get("message", "Data deletion completed"),
            "filters": {"keyword": keyword, "platform": platform}
        }
        
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        logger.error(f"Data deletion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Demo endpoint for testing
@router.post("/demo/notion")
async def demo_notion_crawl():
    """
    Demo endpoint to crawl 'Notion' keyword from Reddit.
    This satisfies the acceptance criteria.
    """
    try:
        result = ugc_crawler.crawl_keyword_simple(
            keyword="Notion",
            platform="reddit",
            max_posts=50
        )
        
        return {
            "message": "Demo crawl completed for 'Notion' keyword",
            "results": result,
            "note": "Check /data endpoint to view collected posts"
        }
        
    except Exception as e:
        logger.error(f"Demo crawl failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# AI Service Endpoints

@router.post("/ai/extract-problems", response_model=ExtractProblemsResponse)
async def extract_problems(request: ExtractProblemsRequest):
    """
    Extract problems from provided text using AI (Google Gemini).
    
    - **text**: The text content to analyze (user reviews, feedback, etc.)
    
    Returns extracted problems with categorization and severity.
    """
    try:
        extractor = ProblemExtractor(api_key=settings.gemini_api_key, model_name=settings.gemini_model)
        result = extractor.extract_problems(request.text)
        return ExtractProblemsResponse(**result)
    except Exception as e:
        logger.error(f"Problem extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/extract-from-ugc", response_model=ExtractFromUGCResponse)
async def extract_from_ugc(request: ExtractFromUGCRequest):
    """
    Crawl UGC and extract problems in one operation.
    
    - **keyword**: Search keyword (e.g., "Notion", "Slack")
    - **platform**: Platform to crawl (reddit, twitter)
    - **limit**: Number of posts to fetch (1-500)
    
    Returns both the crawled content and extracted problems.
    """
    try:
        # Step 1: Determine which crawler to use
        if request.platform not in ["reddit", "twitter", "both"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported platform: {request.platform}. Use 'reddit', 'twitter', or 'both'"
            )
        
        # Step 2: Crawl UGC
        if request.platform == "both":
            # Use multi-platform crawl
            result = ugc_crawler.crawl_all_platforms(
                keyword=request.keyword,
                max_posts_per_platform=request.limit,
                include_comments=False,
                subreddits=None,
                days_back=7
            )
            
            # Collect all posts
            all_posts = []
            for platform_name, platform_data in result.get("platforms", {}).items():
                if platform_data.get("status") == "completed":
                    posts = platform_data.get("posts", [])
                    all_posts.extend(posts)
        else:
            # Use single platform crawl
            result = ugc_crawler.crawl_keyword_simple(
                keyword=request.keyword,
                platform=request.platform,
                max_posts=request.limit
            )
            all_posts = result.get("posts", [])
        
        if not all_posts:
            raise HTTPException(
                status_code=404, 
                detail=f"No posts found for keyword '{request.keyword}'"
            )
        
        # Step 3: Combine text from all posts
        combined_text = "\n\n".join([
            f"Post: {post.get('title', '')} {post.get('content', '')}"
            for post in all_posts
            if post.get('title') or post.get('content')
        ])
        
        if not combined_text.strip():
            raise HTTPException(
                status_code=400, 
                detail="No text content found in crawled posts"
            )
        
        logger.info(f"Analyzing {len(all_posts)} posts with {len(combined_text)} characters")
        
        # Step 4: Extract problems using AI
        extractor = ProblemExtractor(api_key=settings.gemini_api_key, model_name=settings.gemini_model)
        problems_result = extractor.extract_problems(combined_text)
        
        return ExtractFromUGCResponse(
            keyword=request.keyword,
            platform=request.platform,
            total_posts_analyzed=len(all_posts),
            problems=problems_result.get("problems", []),
            summary=problems_result.get("summary", {}),
            crawled_at=datetime.utcnow().isoformat() + "Z"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Extract from UGC failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/batch-extract")
async def batch_extract_problems(texts: List[str]):
    """
    Extract problems from multiple text sources in batch.
    
    - **texts**: List of text strings to analyze
    
    Returns a list of extraction results.
    """
    try:
        if not texts:
            raise HTTPException(status_code=400, detail="No texts provided")
        
        if len(texts) > 50:
            raise HTTPException(
                status_code=400, 
                detail="Maximum 50 texts allowed per batch request"
            )
        
        extractor = ProblemExtractor(api_key=settings.gemini_api_key, model_name=settings.gemini_model)
        results = extractor.batch_extract_problems(texts)
        
        return {
            "total_texts": len(texts),
            "results": results,
            "completed_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/problems/mine", response_model=MineProblemsResponse)
async def mine_competitor_problems(request: MineProblemsRequest):
    """
    🎯 LIVE AI PROBLEM EXTRACTION PIPELINE
    
    Orchestrates the complete flow from competitor name to actionable problem insights:
    1. Crawls user-generated content from specified platforms
    2. Aggregates text from all collected posts
    3. Extracts problems using AI (Google Gemini)
    4. Returns structured problem statements with metadata
    
    **Use Case**: Get instant insights about competitor pain points from real user feedback.
    
    **Parameters**:
    - **competitor_name**: Name of the competitor product/service (e.g., "Notion", "Slack", "Asana")
    - **platforms**: List of platforms to search (default: ["reddit", "twitter"])
    - **max_posts**: Maximum posts to analyze per platform (1-500, default: 100)
    - **include_comments**: Include comments/replies in analysis (default: False)
    
    **Returns**: Structured list of problem statements with categories, severity, and impact analysis.
    
    **Example**:
    ```json
    {
        "competitor_name": "Notion",
        "platforms": ["reddit", "twitter"],
        "max_posts": 100
    }
    ```
    """
    try:
        logger.info(f"Starting problem mining pipeline for competitor: {request.competitor_name}")
        
        # Track pipeline execution metadata
        pipeline_start = datetime.utcnow()
        metadata = {
            "crawl_duration_seconds": 0,
            "extraction_duration_seconds": 0,
            "total_duration_seconds": 0,
            "platforms_used": request.platforms,
            "posts_per_platform": {}
        }
        
        # Validate platforms
        supported_platforms = ["reddit", "twitter"]
        invalid_platforms = [p for p in request.platforms if p not in supported_platforms]
        if invalid_platforms:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported platforms: {invalid_platforms}. Supported: {supported_platforms}"
            )
        
        # STEP 1: Crawl UGC from multiple platforms
        logger.info(f"Step 1: Crawling {len(request.platforms)} platform(s) for '{request.competitor_name}'")
        crawl_start = datetime.utcnow()
        
        all_posts = []
        platforms_searched = []
        
        for platform in request.platforms:
            try:
                logger.info(f"Crawling {platform} for '{request.competitor_name}'...")
                
                result = ugc_crawler.crawl_keyword_simple(
                    keyword=request.competitor_name,
                    platform=platform,
                    max_posts=request.max_posts
                )
                
                posts = result.get("posts", [])
                all_posts.extend(posts)
                platforms_searched.append(platform)
                metadata["posts_per_platform"][platform] = len(posts)
                
                logger.info(f"Collected {len(posts)} posts from {platform}")
                
            except Exception as e:
                logger.warning(f"Failed to crawl {platform}: {e}")
                metadata["posts_per_platform"][platform] = 0
        
        crawl_duration = (datetime.utcnow() - crawl_start).total_seconds()
        metadata["crawl_duration_seconds"] = round(crawl_duration, 2)
        
        if not all_posts:
            raise HTTPException(
                status_code=404,
                detail=f"No posts found for competitor '{request.competitor_name}' on any platform"
            )
        
        logger.info(f"Total posts collected: {len(all_posts)}")
        
        # STEP 2: Aggregate text from all posts
        logger.info("Step 2: Aggregating text content from collected posts")
        
        text_parts = []
        for post in all_posts:
            title = post.get('title', '').strip()
            content = post.get('content', '').strip()
            
            if title and content:
                text_parts.append(f"{title}\n{content}")
            elif title:
                text_parts.append(title)
            elif content:
                text_parts.append(content)
        
        combined_text = "\n\n---\n\n".join(text_parts)
        
        if not combined_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text content found in crawled posts"
            )
        
        logger.info(f"Aggregated {len(combined_text)} characters from {len(text_parts)} posts")
        
        # STEP 3: Extract problems using AI
        logger.info("Step 3: Extracting problems using AI (Google Gemini)")
        extraction_start = datetime.utcnow()
        
        extractor = ProblemExtractor(api_key=settings.gemini_api_key, model_name=settings.gemini_model)
        problems_result = extractor.extract_problems(combined_text)
        
        extraction_duration = (datetime.utcnow() - extraction_start).total_seconds()
        metadata["extraction_duration_seconds"] = round(extraction_duration, 2)
        
        # STEP 4: Build response
        total_duration = (datetime.utcnow() - pipeline_start).total_seconds()
        metadata["total_duration_seconds"] = round(total_duration, 2)
        
        logger.info(f"Pipeline completed: {len(problems_result.get('problems', []))} problems extracted")
        
        return MineProblemsResponse(
            competitor_name=request.competitor_name,
            platforms_searched=platforms_searched,
            total_posts_analyzed=len(all_posts),
            problems=problems_result.get("problems", []),
            summary=problems_result.get("summary", {}),
            pipeline_metadata=metadata,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Problem mining pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

