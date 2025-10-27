import praw
from typing import List, Dict
from datetime import datetime
from loguru import logger

class RedditCrawler:
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        self.reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
        logger.info("Reddit client initialized")
    
    def crawl_keyword(self, keyword: str, max_posts: int = 100, include_comments: bool = False) -> Dict:
        posts = []
        for submission in self.reddit.subreddit("all").search(keyword, limit=max_posts):
            posts.append({
                "id": submission.id,
                "title": submission.title,
                "content": submission.selftext,
                "author": str(submission.author) if submission.author else "[deleted]",
                "subreddit": str(submission.subreddit),
                "score": submission.score,
                "num_comments": submission.num_comments,
                "created_utc": datetime.fromtimestamp(submission.created_utc).isoformat(),
                "permalink": f"https://reddit.com{submission.permalink}",
                "platform": "reddit"
            })
        return {"keyword": keyword, "platform": "reddit", "posts": posts, "total_posts": len(posts), "comments": [], "total_comments": 0, "timestamp": datetime.utcnow().isoformat() + "Z"}
