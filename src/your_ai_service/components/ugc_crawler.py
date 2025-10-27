import json
from pathlib import Path
from datetime import datetime
from loguru import logger
from .reddit_crawler import RedditCrawler
from ..config import settings

class UGCCrawler:
    def crawl_all_platforms(self, keyword: str, platforms: list, max_posts_per_platform: int = 50, include_comments: bool = False, subreddits: list = None, days_back: int = None) -> dict:
        """
        Crawl multiple platforms for a given keyword.
        Args:
            keyword: Search term
            platforms: List of platforms (e.g., ["reddit", "twitter"])
            max_posts_per_platform: Max posts per platform
            include_comments: Whether to include comments
            subreddits: List of subreddits to target (optional)
            days_back: How many days back to search (optional)
        Returns:
            Dictionary with results per platform
        """
        results = {}
        for platform in platforms:
            if platform == "reddit" and self.reddit_crawler:
                # For now, ignore subreddits/days_back (can be added later)
                results["reddit"] = self.reddit_crawler.crawl_keyword(keyword, max_posts_per_platform, include_comments)
            elif platform == "twitter" and self.twitter_crawler:
                # Twitter crawling not implemented
                results["twitter"] = {"error": "Twitter crawler not implemented"}
            else:
                results[platform] = {"error": f"Platform '{platform}' not supported or not initialized"}
        return results
    def __init__(self):
           self.reddit_crawler = RedditCrawler(settings.reddit_client_id, settings.reddit_client_secret, settings.reddit_user_agent)
           self.twitter_crawler = None
    
    def crawl_keyword_simple(self, keyword: str, platform: str = "reddit", max_posts: int = 100) -> dict:
        if platform == "reddit":
            return self.reddit_crawler.crawl_keyword(keyword, max_posts)
        raise ValueError(f"Platform '{platform}' not supported")
    
    def save_to_file(self, data: dict, output_path: str = None) -> str:
        if not output_path:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            keyword = data.get("keyword", "unknown").replace(" ", "_")
            output_path = f"data/ugc_{keyword}_{timestamp}.json"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved to: {output_path}")
        return output_path
    
    def get_crawl_stats(self) -> dict:
        """Get crawling statistics. Note: Database functionality not implemented."""
        return {
            "crawl_sessions": {},
            "posts": {"total": 0},
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "note": "Database functionality not implemented in simplified crawler"
        }
    
    def export_data(self, keyword: str = None, platform: str = None, format: str = "json", filename: str = None) -> str:
        """
        Export data from saved JSON files in the data/ directory.
        This is a simplified implementation that reads from saved crawl files.
        """
        import glob
        import csv
        
        # Find matching JSON files
        pattern = "data/ugc_"
        if keyword:
            pattern += f"{keyword}_"
        pattern += "*.json"
        
        files = glob.glob(pattern)
        if not files:
            return None  # No data found
        
        # Collect all posts from matching files
        all_posts = []
        for file in files:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                posts = data.get("posts", [])
                
                # Filter by platform if specified
                if platform:
                    posts = [p for p in posts if p.get("platform") == platform]
                
                all_posts.extend(posts)
        
        if not all_posts:
            return None
        
        # Generate filename
        if not filename:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{keyword or 'all'}_{timestamp}"
        
        # Export based on format
        if format == "json":
            filepath = f"data/exports/{filename}.json"
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({"posts": all_posts, "count": len(all_posts)}, f, indent=2, ensure_ascii=False)
        
        elif format == "csv":
            filepath = f"data/exports/{filename}.csv"
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            # Get all unique keys from posts
            if all_posts:
                fieldnames = list(all_posts[0].keys())
                
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(all_posts)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Exported {len(all_posts)} posts to {filepath}")
        return filepath
    
    def get_crawled_data(self, keyword: str = None, platform: str = None, limit: int = 100, start_date = None, end_date = None) -> list:
        """
        Get crawled data from saved JSON files in the data/ directory.
        This is a simplified implementation that reads from saved crawl files.
        """
        import glob
        
        # Find matching JSON files
        pattern = "data/ugc_"
        if keyword:
            pattern += f"{keyword}_"
        pattern += "*.json"
        
        files = glob.glob(pattern)
        if not files:
            return []
        
        # Collect all posts from matching files
        all_posts = []
        for file in files:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                posts = data.get("posts", [])
                
                # Filter by platform if specified
                if platform:
                    posts = [p for p in posts if p.get("platform") == platform]
                
                all_posts.extend(posts)
        
        # Apply limit
        return all_posts[:limit]
    
    def delete_data(self, keyword: str = None, platform: str = None) -> dict:
        """Delete crawled data. Note: Database functionality not implemented."""
        raise NotImplementedError("Delete functionality requires database integration")
