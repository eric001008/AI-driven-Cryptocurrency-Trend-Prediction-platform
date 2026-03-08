import os
import praw
from dotenv import load_dotenv

load_dotenv()

# Reading Reddit API credentials from environment variables
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="reddit-sentiment-test"
)

# Search subreddit for new posts
subreddit = reddit.subreddit("CryptoCurrency")

print("Fetching latest posts...\n")
for post in subreddit.new(limit=5):
    print(f"Title: {post.title}")
    print(f"Author: {post.author}")
    print(f"Content: {post.selftext[:100]}...")
    print(f"Created (UTC): {post.created_utc}")
    print(f"Score: {post.score}")
    print(f"Comments: {post.num_comments}")
    print(f"Permalink: https://reddit.com{post.permalink}")
    print("-" * 60)
