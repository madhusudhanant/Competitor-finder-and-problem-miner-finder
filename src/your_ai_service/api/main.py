"""
Main FastAPI application for UGC Crawler service.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from ..config import settings
from .v1.endpoints import router as v1_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    logger.info("Starting Competitor Finder - UGC Problem Miner API")
    logger.info(f"API docs available at: http://{settings.api_host}:{settings.api_port}/docs")
    yield
    # Shutdown
    logger.info("Shutting down Competitor Finder API")

# Create FastAPI app
app = FastAPI(
    title="Competitor Finder - UGC Problem Miner API",
    description="API for crawling User-Generated Content from Reddit and Twitter for problem mining with AI-powered analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(v1_router, prefix="/api/v1", tags=["UGC Crawler & AI Analysis"])

@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "service": "Competitor Finder - UGC Problem Miner",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "api": "/api/v1",
        "features": [
            "Crawl user-generated content from Reddit and Twitter",
            "Extract problems from text using Google Gemini AI",
            "Combined UGC crawling and problem extraction",
            "Data storage and export"
        ]
    }

