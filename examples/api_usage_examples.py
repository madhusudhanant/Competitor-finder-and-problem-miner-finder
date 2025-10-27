"""
Example usage of the Competitor Finder API.

This script demonstrates how to use the API programmatically with Python.
Make sure the API server is running (python main.py) before running this script.
"""
import requests
import json
from typing import Dict, List


class CompetitorFinderClient:
    """Python client for the Competitor Finder API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the client with API base URL."""
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
    
    def check_health(self) -> Dict:
        """Check if the API is healthy."""
        response = requests.get(f"{self.api_url}/health")
        response.raise_for_status()
        return response.json()
    
    def extract_problems(self, text: str) -> Dict:
        """
        Extract problems from text using AI.
        
        Args:
            text: The text to analyze
        
        Returns:
            Dictionary with problems and summary
        """
        response = requests.post(
            f"{self.api_url}/ai/extract-problems",
            json={"text": text}
        )
        response.raise_for_status()
        return response.json()
    
    def extract_from_ugc(
        self, 
        keyword: str, 
        platform: str = "reddit", 
        limit: int = 50
    ) -> Dict:
        """
        Crawl UGC and extract problems in one call.
        
        Args:
            keyword: Search keyword
            platform: Platform to crawl (reddit, twitter, both)
            limit: Number of posts to fetch
        
        Returns:
            Dictionary with crawled data and extracted problems
        """
        response = requests.post(
            f"{self.api_url}/ai/extract-from-ugc",
            json={
                "keyword": keyword,
                "platform": platform,
                "limit": limit
            }
        )
        response.raise_for_status()
        return response.json()
    
    def batch_extract(self, texts: List[str]) -> Dict:
        """
        Extract problems from multiple texts in batch.
        
        Args:
            texts: List of text strings to analyze
        
        Returns:
            Dictionary with batch results
        """
        response = requests.post(
            f"{self.api_url}/ai/batch-extract",
            json=texts
        )
        response.raise_for_status()
        return response.json()
    
    def crawl_simple(
        self, 
        keyword: str, 
        platform: str = "reddit", 
        max_posts: int = 50
    ) -> Dict:
        """
        Simple crawl from a single platform.
        
        Args:
            keyword: Search keyword
            platform: Platform to crawl (reddit or twitter)
            max_posts: Maximum posts to fetch
        
        Returns:
            Dictionary with crawl results
        """
        response = requests.post(
            f"{self.api_url}/crawl/simple",
            json={
                "keyword": keyword,
                "platform": platform,
                "max_posts": max_posts
            }
        )
        response.raise_for_status()
        return response.json()


def example_1_extract_from_text():
    """Example 1: Extract problems from a text string."""
    print("\n" + "="*60)
    print("Example 1: Extract Problems from Text")
    print("="*60)
    
    client = CompetitorFinderClient()
    
    sample_text = """
    I've been using Notion for 6 months and while I love the concept,
    there are several issues. The mobile app is incredibly slow and 
    often crashes when syncing large databases. The offline mode barely
    works - I lose data if I edit while offline. The learning curve is
    steep and the documentation could be better. Also, it's expensive
    for teams. Customer support takes days to respond.
    """
    
    print("\n📝 Analyzing text...")
    result = client.extract_problems(sample_text)
    
    print(f"\n✅ Found {len(result['problems'])} problems:")
    for i, problem in enumerate(result['problems'], 1):
        print(f"\n{i}. {problem['problem_statement']}")
        print(f"   Category: {problem['category']}")
        print(f"   Severity: {problem['severity']}")
        print(f"   Impact: {problem['user_impact']}")
    
    print(f"\n📊 Summary:")
    print(f"   Total Problems: {result['summary']['total_problems']}")
    print(f"   Most Common: {result['summary'].get('most_common_category', 'N/A')}")
    print(f"   Sentiment: {result['summary'].get('overall_sentiment', 'N/A')}")


def example_2_extract_from_reddit():
    """Example 2: Crawl Reddit and extract problems."""
    print("\n" + "="*60)
    print("Example 2: Crawl Reddit + Extract Problems")
    print("="*60)
    
    client = CompetitorFinderClient()
    
    keyword = "Notion"
    print(f"\n🔍 Crawling Reddit for '{keyword}'...")
    print("   This may take 30-60 seconds...")
    
    try:
        result = client.extract_from_ugc(
            keyword=keyword,
            platform="reddit",
            limit=30
        )
        
        print(f"\n✅ Analyzed {result['total_posts_analyzed']} posts")
        print(f"   Found {len(result['problems'])} problems:")
        
        for i, problem in enumerate(result['problems'][:5], 1):  # Show top 5
            print(f"\n{i}. {problem['problem_statement']}")
            print(f"   Severity: {problem['severity']}")
        
        if len(result['problems']) > 5:
            print(f"\n   ... and {len(result['problems']) - 5} more problems")
        
    except requests.exceptions.HTTPException as e:
        print(f"\n❌ Error: {e}")
        print("   Make sure Reddit credentials are configured in .env")


def example_3_batch_processing():
    """Example 3: Process multiple texts in batch."""
    print("\n" + "="*60)
    print("Example 3: Batch Processing")
    print("="*60)
    
    client = CompetitorFinderClient()
    
    reviews = [
        "The app crashes every time I try to export data. Very frustrating!",
        "Love the features but the UI is confusing. Can't find basic settings.",
        "Great product but way too expensive for small teams."
    ]
    
    print(f"\n📚 Processing {len(reviews)} reviews in batch...")
    result = client.batch_extract(reviews)
    
    print(f"\n✅ Processed {result['total_texts']} texts:")
    for i, review_result in enumerate(result['results'], 1):
        problems = review_result.get('problems', [])
        print(f"\n{i}. Review {i}: Found {len(problems)} problem(s)")
        for problem in problems:
            print(f"   - {problem['problem_statement']}")


def example_4_crawl_only():
    """Example 4: Just crawl without AI analysis."""
    print("\n" + "="*60)
    print("Example 4: Crawl Reddit (No AI Analysis)")
    print("="*60)
    
    client = CompetitorFinderClient()
    
    keyword = "Slack"
    print(f"\n🔍 Crawling Reddit for '{keyword}'...")
    
    try:
        result = client.crawl_simple(
            keyword=keyword,
            platform="reddit",
            max_posts=20
        )
        
        print(f"\n✅ Crawled {result['total_collected']} posts")
        print(f"   Status: {result['status']}")
        
        # You can now process these posts however you want
        
    except requests.exceptions.HTTPException as e:
        print(f"\n❌ Error: {e}")
        print("   Make sure Reddit credentials are configured in .env")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("COMPETITOR FINDER API - USAGE EXAMPLES")
    print("="*60)
    
    client = CompetitorFinderClient()
    
    # Check if API is running
    try:
        health = client.check_health()
        print(f"\n✅ API is running!")
        print(f"   Status: {health['status']}")
        print(f"   Version: {health['version']}")
        print(f"   Reddit Available: {health['reddit_available']}")
        print(f"   Twitter Available: {health['twitter_available']}")
    except requests.exceptions.RequestException:
        print("\n❌ ERROR: API is not running!")
        print("\n   Please start the API server first:")
        print("   python main.py")
        return
    
    # Run examples
    try:
        # Example 1: Always works (no social media required)
        example_1_extract_from_text()
        
        # Example 2: Requires Reddit credentials
        if health.get('reddit_available'):
            example_2_extract_from_reddit()
        else:
            print("\n⚠️  Skipping Example 2 (Reddit not configured)")
        
        # Example 3: Always works
        example_3_batch_processing()
        
        # Example 4: Requires Reddit credentials
        if health.get('reddit_available'):
            example_4_crawl_only()
        else:
            print("\n⚠️  Skipping Example 4 (Reddit not configured)")
        
        print("\n" + "="*60)
        print("✅ All examples completed!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
