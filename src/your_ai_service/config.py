"""
Configuration management for the UGC Problem Miner service.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation."""
    
    # AI Service settings
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    
    # Reddit API settings
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "UGCCrawler/1.0"
    
    # Twitter API settings
    twitter_bearer_token: str = ""
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    twitter_access_token: str = ""
    twitter_access_token_secret: str = ""
    
    # Database settings
    database_url: str = "sqlite:///./ugc_data.db"
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "competitor_finder"
    
    # Application settings
    log_level: str = "INFO"
    max_posts_per_request: int = 100
    rate_limit_delay: int = 1
    
    # Data storage settings
    data_dir: str = "./data"
    export_format: str = "json"  # json, csv, or both
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()