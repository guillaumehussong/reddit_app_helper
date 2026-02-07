#!/usr/bin/env python3
"""
Reddit Subreddit Monitor
========================
A simple monitoring tool that fetches recent posts from specified subreddits
and filters them by keywords. Designed for personal use / research only.

Usage:
    python main.py
    python main.py --subreddit python --limit 20
    python main.py --subreddit python --keywords "async,typing,pep"
"""

import argparse
import logging
import os
import sys
from datetime import datetime, timezone

import praw
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

load_dotenv()  # Load credentials from .env file

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

DEFAULT_SUBREDDIT = "python"
DEFAULT_LIMIT = 10
DEFAULT_KEYWORDS: list[str] = []


def get_reddit_client() -> praw.Reddit:
    """Create and return an authenticated Reddit (read-only) client."""
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")

    if not all([client_id, client_secret, user_agent]):
        logger.error(
            "Missing Reddit API credentials. "
            "Please set REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, and "
            "REDDIT_USER_AGENT in your .env file. "
            "See .env.example for reference."
        )
        sys.exit(1)

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )
    reddit.read_only = True  # We only need read access
    logger.info("Reddit client initialized (read-only mode)")
    return reddit


def fetch_recent_posts(
    reddit: praw.Reddit,
    subreddit_name: str,
    limit: int = DEFAULT_LIMIT,
) -> list[praw.models.Submission]:
    """Fetch the most recent posts from a subreddit."""
    logger.info("Fetching %d latest posts from r/%s ...", limit, subreddit_name)
    subreddit = reddit.subreddit(subreddit_name)
    posts = list(subreddit.new(limit=limit))
    logger.info("Fetched %d posts", len(posts))
    return posts


def filter_by_keywords(
    posts: list[praw.models.Submission],
    keywords: list[str],
) -> list[praw.models.Submission]:
    """Filter posts whose title contains at least one keyword (case-insensitive)."""
    if not keywords:
        return posts

    keywords_lower = [kw.lower().strip() for kw in keywords]
    matched = [
        post
        for post in posts
        if any(kw in post.title.lower() for kw in keywords_lower)
    ]
    logger.info(
        "Keyword filter: %d/%d posts matched keywords %s",
        len(matched),
        len(posts),
        keywords_lower,
    )
    return matched


def display_posts(posts: list[praw.models.Submission]) -> None:
    """Pretty-print a list of posts to the console."""
    if not posts:
        logger.info("No posts to display.")
        return

    separator = "-" * 72
    print(f"\n{'='*72}")
    print(f" {'MATCHED POSTS':^70}")
    print(f"{'='*72}\n")

    for idx, post in enumerate(posts, start=1):
        created = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
        print(f"  [{idx}] {post.title}")
        print(f"      Author : u/{post.author}")
        print(f"      Score  : {post.score}  |  Comments: {post.num_comments}")
        print(f"      Date   : {created:%Y-%m-%d %H:%M:%S UTC}")
        print(f"      URL    : https://reddit.com{post.permalink}")
        print(f"      {separator}")

    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Monitor a subreddit for recent posts matching keywords.",
    )
    parser.add_argument(
        "-s",
        "--subreddit",
        default=DEFAULT_SUBREDDIT,
        help=f"Subreddit to monitor (default: {DEFAULT_SUBREDDIT})",
    )
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"Number of recent posts to fetch (default: {DEFAULT_LIMIT})",
    )
    parser.add_argument(
        "-k",
        "--keywords",
        default="",
        help='Comma-separated keywords to filter on (e.g. "async,typing,pep")',
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    args = parse_args()

    keywords = [kw for kw in args.keywords.split(",") if kw.strip()] if args.keywords else DEFAULT_KEYWORDS

    reddit = get_reddit_client()
    posts = fetch_recent_posts(reddit, args.subreddit, args.limit)
    matched = filter_by_keywords(posts, keywords)
    display_posts(matched)


if __name__ == "__main__":
    main()
