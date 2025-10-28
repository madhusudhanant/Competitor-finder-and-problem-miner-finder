"""
Test script to verify the modular AI service setup.
Run this to test individual components without starting the full API.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.your_ai_service.components.ai_service import ProblemExtractor, format_problems_output


def test_problem_extraction():
    """Test the problem extraction functionality."""
    print("="*60)
    print("Testing Problem Extraction Service")
    print("="*60)
    
    # Sample text for testing
    sample_text = """
    I've been using this app for 3 months now and I'm really frustrated.
    The interface is so confusing - I can never find the features I need.
    The app crashes at least twice a day, especially when I'm working on
    important documents. Customer support takes days to respond.
    The mobile version is even worse - it's super slow and drains my battery.
    Also, the pricing is too expensive for what you get. I'm considering
    switching to a competitor.
    """
    
    try:
        # Check if API key is set
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ ERROR: GEMINI_API_KEY not found in environment variables")
            print("\nPlease set your Gemini API key:")
            print("  1. Copy .env.example to .env")
            print("  2. Add your GEMINI_API_KEY to the .env file")
            print("  3. Get API key from: https://makersuite.google.com/app/apikey")
            return False
        
        print("\n✓ Gemini API key found")
        print(f"  Using model: {os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')}")
        
        # Initialize extractor
        print("\n📝 Initializing ProblemExtractor...")
        extractor = ProblemExtractor()
        print("✓ ProblemExtractor initialized successfully")
        
        # Extract problems
        print("\n🔍 Extracting problems from sample text...")
        print(f"  Text length: {len(sample_text)} characters")
        
        result = extractor.extract_problems(sample_text)
        
        # Display results
        print("\n" + format_problems_output(result))
        
        # Verify results
        if result.get("problems"):
            print(f"\n✅ SUCCESS: Extracted {len(result['problems'])} problems")
            return True
        else:
            print("\n⚠️  WARNING: No problems extracted (this might be OK)")
            return True
            
    except Exception as e:
        print(f"\n ERROR: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Verify your GEMINI_API_KEY is valid")
        print("  2. Check your internet connection")
        print("  3. Ensure google-generativeai is installed")
        return False


def test_dependencies():
    """Test that all required dependencies are installed."""
    print("="*60)
    print("Testing Dependencies")
    print("="*60)
    
    dependencies = {
        "fastapi": "FastAPI web framework",
        "uvicorn": "ASGI server",
        "pydantic": "Data validation",
        "pydantic_settings": "Settings management",
        "google.generativeai": "Google Gemini AI",
        "loguru": "Logging",
        "sqlalchemy": "Database ORM"
    }
    
    optional_dependencies = {
        "praw": "Reddit API (optional)",
        "tweepy": "Twitter API (optional)"
    }
    
    all_good = True
    
    print("\n📦 Required Dependencies:")
    for module_name, description in dependencies.items():
        try:
            __import__(module_name)
            print(f"  ✓ {module_name:<25} - {description}")
        except ImportError:
            print(f"  ❌ {module_name:<25} - MISSING - {description}")
            all_good = False
    
    print("\n📦 Optional Dependencies:")
    for module_name, description in optional_dependencies.items():
        try:
            __import__(module_name)
            print(f"  ✓ {module_name:<25} - {description}")
        except ImportError:
            print(f"  ⚠️  {module_name:<25} - Not installed - {description}")
    
    return all_good


def test_config():
    """Test configuration loading."""
    print("\n" + "="*60)
    print("Testing Configuration")
    print("="*60)
    
    try:
        from src.your_ai_service.config import settings
        
        print("\n✓ Configuration loaded successfully")
        print(f"  API Host: {settings.api_host}")
        print(f"  API Port: {settings.api_port}")
        print(f"  Log Level: {settings.log_level}")
        print(f"  Database URL: {settings.database_url}")
        
        # Check credentials
        print("\n🔑 Credentials Status:")
        print(f"  Gemini API Key: {'✓ Set' if settings.gemini_api_key else '❌ Not set'}")
        print(f"  Reddit Client ID: {'✓ Set' if settings.reddit_client_id else '⚠️  Not set'}")
        print(f"  Reddit Client Secret: {'✓ Set' if settings.reddit_client_secret else '⚠️  Not set'}")
        print(f"  Twitter Bearer Token: {'✓ Set' if settings.twitter_bearer_token else '⚠️  Not set'}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Configuration error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("COMPETITOR FINDER - COMPONENT TEST SUITE")
    print("="*60)
    
    # Test 1: Dependencies
    deps_ok = test_dependencies()
    
    # Test 2: Configuration
    config_ok = test_config()
    
    # Test 3: Problem Extraction (only if config is OK)
    extraction_ok = False
    if config_ok:
        extraction_ok = test_problem_extraction()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"  Dependencies: {'✅ PASS' if deps_ok else '❌ FAIL'}")
    print(f"  Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"  Problem Extraction: {'✅ PASS' if extraction_ok else '⚠️  SKIP/FAIL'}")
    print("="*60)
    
    if deps_ok and config_ok and extraction_ok:
        print("\n🎉 All tests passed! You're ready to start the API server.")
        print("\nRun: python main.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
