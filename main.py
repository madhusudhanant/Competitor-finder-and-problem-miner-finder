"""
Main entry point for the Competitor Finder API.
Run with: python main.py
"""
import uvicorn
from src.your_ai_service.config import settings

if __name__ == "__main__":
    print("="*60)
    print("Starting Competitor Finder API")
    print("="*60)
    print(f"API Documentation: http://{settings.api_host}:{settings.api_port}/docs")
    print(f"ReDoc: http://{settings.api_host}:{settings.api_port}/redoc")
    print("="*60)
    
    uvicorn.run(
        "src.your_ai_service.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )

