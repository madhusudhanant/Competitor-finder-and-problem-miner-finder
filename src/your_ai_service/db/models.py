"""
Database models for storing UGC data.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()


class UGCPost(Base):
    """Model for storing UGC posts from various platforms."""
    
    __tablename__ = "ugc_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Platform information
    platform = Column(String(50), nullable=False, index=True)  # reddit, twitter, etc.
    platform_post_id = Column(String(255), nullable=False, unique=True, index=True)
    
    # Search/crawl information
    search_keyword = Column(String(255), nullable=False, index=True)
    
    # Content
    title = Column(String(500))
    content = Column(Text, nullable=False)
    author = Column(String(255))
    url = Column(String(1000))
    
    # Metadata
    created_at = Column(DateTime, nullable=False)
    crawled_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Engagement metrics
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    
    # Analysis fields
    sentiment_score = Column(Float)
    is_problem_related = Column(Boolean)
    problem_category = Column(String(255))
    
    # Additional metadata as JSON string
    raw_data = Column(Text)  # Store original API response
    
    def __repr__(self) -> str:
        return f"<UGCPost(platform={self.platform}, keyword={self.search_keyword}, author={self.author})>"


class CrawlSession(Base):
    """Model for tracking crawling sessions."""
    
    __tablename__ = "crawl_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False)
    search_keyword = Column(String(255), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
    posts_collected = Column(Integer, default=0)
    status = Column(String(50), default="running")  # running, completed, failed
    error_message = Column(Text)
    
    def __repr__(self) -> str:
        return f"<CrawlSession(platform={self.platform}, keyword={self.search_keyword}, status={self.status})>"