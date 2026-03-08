import os
import praw

# Initializing the Reddit client
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="crypto-research-bot by u/Miserable-Bed-939"
)

def fetch_reddit(cur, subreddit_name="CryptoCurrency", limit=10):
    """
    Get posts from the specified subreddit and write them to the PostgreSQL table ods.reddit
    """
    try:
        posts = reddit.subreddit(subreddit_name).new(limit=limit)
        for post in posts:
            cur.execute(
                """
                INSERT INTO ods.media_reddit_posts (
                    id, title, content, author, subreddit,
                    created_utc, score, upvote_ratio, num_comments,
                    url, permalink
                ) VALUES (%s, %s, %s, %s, %s, to_timestamp(%s), %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
                """,
                (
                    post.id,
                    post.title,
                    post.selftext,
                    str(post.author) if post.author else None,
                    post.subreddit.display_name,
                    post.created_utc,
                    post.score,
                    post.upvote_ratio,
                    post.num_comments,
                    post.url,
                    post.permalink
                )
            )
    except Exception as e:
        print(f"Failed to fetch Reddit data: {e}")
