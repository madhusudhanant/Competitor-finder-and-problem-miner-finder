"""
UGC Crawler CLI

Command-line tool to crawl user-generated content from Reddit/Twitter.

Usage:
    python crawl_ugc.py "Notion" --platform reddit --count 100
    python crawl_ugc.py "Slack" --platform reddit --count 50 --save
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from your_ai_service.components.ugc_crawler import UGCCrawler
from loguru import logger


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Crawl user-generated content from Reddit/Twitter"
    )
    
    parser.add_argument(
        "keyword",
        type=str,
        help="Keyword or competitor name to search for (e.g., 'Notion')"
    )
    
    parser.add_argument(
        "--platform",
        type=str,
        default="reddit",
        choices=["reddit", "twitter"],
        help="Platform to crawl (default: reddit)"
    )
    
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Maximum number of posts to fetch (default: 100)"
    )
    
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save results to a JSON file in data/ directory"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Custom output file path (implies --save)"
    )
    
    args = parser.parse_args()
    
    # Initialize crawler
    logger.info("Initializing UGC crawler...")
    crawler = UGCCrawler()
    
    # Run crawl
    logger.info(f"Crawling {args.platform} for keyword: '{args.keyword}'")
    logger.info(f"Target posts: {args.count}")
    
    try:
        result = crawler.crawl_keyword_simple(
            keyword=args.keyword,
            platform=args.platform,
            max_posts=args.count
        )
        
        # Display summary
        print("\n" + "="*60)
        print("CRAWL RESULTS")
        print("="*60)
        print(f"Keyword: {result.get('keyword')}")
        print(f"Platform: {result.get('platform')}")
        print(f"Posts found: {result.get('total_posts', 0)}")
        print(f"Comments found: {result.get('total_comments', 0)}")
        print(f"Duration: {result.get('crawl_duration_seconds', 0):.2f} seconds")
        print("="*60)
        
        # Show sample posts
        posts = result.get('posts', [])
        if posts:
            print(f"\nSample posts (showing first 3 of {len(posts)}):")
            for i, post in enumerate(posts[:3], 1):
                print(f"\n{i}. {post.get('title', 'No title')}")
                print(f"   Subreddit: r/{post.get('subreddit')}")
                print(f"   Score: {post.get('score')} | Comments: {post.get('num_comments')}")
                content_preview = post.get('content', '')[:100]
                if content_preview:
                    print(f"   Preview: {content_preview}...")
        
        # Save to file if requested
        if args.save or args.output:
            output_path = crawler.save_to_file(result, args.output)
            print(f"\n✓ Results saved to: {output_path}")
        
        print("\n✓ Crawl completed successfully!")
        
    except Exception as e:
        logger.error(f"Crawl failed: {e}")
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
