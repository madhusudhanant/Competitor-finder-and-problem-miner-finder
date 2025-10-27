"""
Pydantic schemas for API request/response models.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CrawlRequest(BaseModel):
    """Request model for crawling operations."""
    keyword: str = Field(..., description="Search keyword or phrase")
    platforms: List[str] = Field(default=["reddit"], description="Platforms to crawl (reddit, twitter)")
    max_posts_per_platform: int = Field(default=50, ge=1, le=500, description="Maximum posts per platform")
    include_comments: bool = Field(default=False, description="Include comments/replies")
    subreddits: Optional[List[str]] = Field(None, description="Specific subreddits for Reddit (optional)")
    days_back: int = Field(default=7, ge=1, le=30, description="Days back to search (Twitter only)")


class SimpleCrawlRequest(BaseModel):
    """Simplified request model for single platform crawling."""
    keyword: str = Field(..., description="Search keyword or phrase")
    platform: str = Field(default="reddit", description="Platform to crawl (reddit or twitter)")
    max_posts: int = Field(default=50, ge=1, le=100, description="Maximum posts to collect")


class CrawlResponse(BaseModel):
    """Response model for crawl operations."""
    session_id: Optional[int] = None
    keyword: str
    status: str
    total_collected: int
    platforms: Dict[str, Any]
    started_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None


class UGCPostResponse(BaseModel):
    """Response model for UGC post data."""
    id: int
    platform: str
    platform_post_id: str
    search_keyword: str
    title: Optional[str]
    content: str
    author: Optional[str]
    url: Optional[str]
    created_at: Optional[datetime]
    crawled_at: Optional[datetime]
    upvotes: int = 0
    downvotes: int = 0
    comments_count: int = 0
    shares_count: int = 0
    likes_count: int = 0
    sentiment_score: Optional[float] = None
    is_problem_related: Optional[bool] = None
    problem_category: Optional[str] = None


class DataQueryRequest(BaseModel):
    """Request model for querying crawled data."""
    keyword: Optional[str] = Field(None, description="Filter by keyword")
    platform: Optional[str] = Field(None, description="Filter by platform")
    limit: Optional[int] = Field(100, ge=1, le=1000, description="Maximum results to return")
    start_date: Optional[datetime] = Field(None, description="Filter by creation date (start)")
    end_date: Optional[datetime] = Field(None, description="Filter by creation date (end)")


class DataQueryResponse(BaseModel):
    """Response model for data queries."""
    total_count: int
    posts: List[UGCPostResponse]
    filters_applied: Dict[str, Any]


class ExportRequest(BaseModel):
    """Request model for data export."""
    keyword: Optional[str] = Field(None, description="Filter by keyword")
    platform: Optional[str] = Field(None, description="Filter by platform")
    format: str = Field(default="json", description="Export format (json, csv)")
    filename: Optional[str] = Field(None, description="Custom filename")


class ExportResponse(BaseModel):
    """Response model for data export."""
    filename: str
    filepath: str
    record_count: int
    format: str
    created_at: str


class StatsResponse(BaseModel):
    """Response model for crawling statistics."""
    crawl_sessions: Dict[str, Any]
    posts: Dict[str, Any]
    last_updated: str


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    timestamp: str
    version: str
    database_connected: bool
    reddit_available: bool
    twitter_available: bool


# AI Service Schemas

class ProblemStatement(BaseModel):
    """Individual problem extracted from text."""
    problem_statement: str
    category: str
    severity: str
    affected_feature: str
    user_impact: str


class ProblemSummary(BaseModel):
    """Summary of extracted problems."""
    total_problems: int
    most_common_category: Optional[str] = None
    overall_sentiment: Optional[str] = None
    error: Optional[str] = None


class ExtractProblemsRequest(BaseModel):
    """Request model for problem extraction."""
    text: str = Field(..., description="Text content to analyze (user reviews, feedback, etc.)")


class ExtractProblemsResponse(BaseModel):
    """Response model for problem extraction."""
    problems: List[ProblemStatement]
    summary: ProblemSummary


class ExtractFromUGCRequest(BaseModel):
    """Request model for extracting problems from UGC."""
    keyword: str = Field(..., description="Search keyword")
    platform: str = Field(default="reddit", description="Platform: reddit, twitter, or both")
    limit: int = Field(default=50, ge=1, le=500, description="Number of posts to fetch")


class ExtractFromUGCResponse(BaseModel):
    """Response model for extracting problems from UGC."""
    keyword: str
    platform: str
    total_posts_analyzed: int
    problems: List[ProblemStatement]
    summary: ProblemSummary
    crawled_at: str


class MineProblemsRequest(BaseModel):
    """Request model for mining problems from a competitor."""
    competitor_name: str = Field(..., description="Name of the competitor product/service")
    platforms: List[str] = Field(default=["reddit", "twitter"], description="Platforms to search (reddit, twitter)")
    max_posts: int = Field(default=100, ge=1, le=500, description="Maximum posts to analyze")
    include_comments: bool = Field(default=False, description="Include comments/replies in analysis")


class MineProblemsResponse(BaseModel):
    """Response model for problem mining pipeline."""
    competitor_name: str
    platforms_searched: List[str]
    total_posts_analyzed: int
    problems: List[ProblemStatement]
    summary: ProblemSummary
    pipeline_metadata: Dict[str, Any] = Field(default_factory=dict, description="Pipeline execution metadata")
    timestamp: str

