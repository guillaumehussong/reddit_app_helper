#!/usr/bin/env python3
"""
Reddit Discussion Discovery Tool
=================================
A simple and respectful tool that helps users discover relevant discussions
and useful information more easily. The app does not manipulate content or
automate interactions. Instead, it focuses on improving access to publicly
available data in a structured and user-friendly way.

Usage:
    python main.py
    python main.py --subreddits python,learnpython --sort hot --limit 15
    python main.py --search "async python" --subreddits python
    python main.py --subreddits python --keywords "async,typing,pep"
"""

import argparse
import logging
import os
import sys
import textwrap
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

DEFAULT_SUBREDDITS = ["python"]
DEFAULT_LIMIT = 10
DEFAULT_KEYWORDS: list[str] = []
DEFAULT_SORT = "hot"
VALID_SORTS = ("hot", "new", "top", "rising")
BODY_PREVIEW_LENGTH = 200


def get_reddit_client() -> praw.Reddit:
    """Create and return an authenticated Reddit client in read-only mode.

    The client is strictly read-only: it does not manipulate content
    or automate any interactions with Reddit.
    """
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
    reddit.read_only = True  # Read-only: no content manipulation
    logger.info("Reddit client initialized (read-only mode)")
    return reddit


# ---------------------------------------------------------------------------
# Data retrieval — read-only access to publicly available data
# ---------------------------------------------------------------------------


def fetch_posts(
    reddit: praw.Reddit,
    subreddit_name: str,
    sort: str = DEFAULT_SORT,
    limit: int = DEFAULT_LIMIT,
) -> list[praw.models.Submission]:
    """Fetch recent posts from a subreddit using the chosen sort order.

    This function only reads publicly available data and does not
    perform any write operations.
    """
    logger.info(
        "Fetching %d %s posts from r/%s ...", limit, sort, subreddit_name
    )
    subreddit = reddit.subreddit(subreddit_name)

    sort_methods = {
        "hot": subreddit.hot,
        "new": subreddit.new,
        "top": subreddit.top,
        "rising": subreddit.rising,
    }

    fetcher = sort_methods.get(sort, subreddit.hot)
    posts = list(fetcher(limit=limit))
    logger.info("Fetched %d posts from r/%s", len(posts), subreddit_name)
    return posts


def fetch_posts_from_multiple(
    reddit: praw.Reddit,
    subreddit_names: list[str],
    sort: str = DEFAULT_SORT,
    limit: int = DEFAULT_LIMIT,
) -> list[praw.models.Submission]:
    """Fetch posts from multiple subreddits to broaden discovery.

    Combines results from several communities so users can discover
    relevant discussions across different sources.
    """
    all_posts: list[praw.models.Submission] = []
    for name in subreddit_names:
        name = name.strip()
        if not name:
            continue
        posts = fetch_posts(reddit, name, sort=sort, limit=limit)
        all_posts.extend(posts)

    logger.info(
        "Total: %d posts fetched from %d subreddit(s)",
        len(all_posts),
        len(subreddit_names),
    )
    return all_posts


def search_discussions(
    reddit: praw.Reddit,
    query: str,
    subreddit_names: list[str],
    sort: str = "relevance",
    limit: int = DEFAULT_LIMIT,
) -> list[praw.models.Submission]:
    """Search for relevant discussions matching a query.

    Helps users discover discussions and useful information more easily
    by searching publicly available Reddit data.
    """
    all_results: list[praw.models.Submission] = []
    search_sort = sort if sort in ("relevance", "hot", "top", "new") else "relevance"

    for name in subreddit_names:
        name = name.strip()
        if not name:
            continue
        logger.info(
            'Searching r/%s for "%s" (sort=%s, limit=%d) ...',
            name,
            query,
            search_sort,
            limit,
        )
        subreddit = reddit.subreddit(name)
        results = list(subreddit.search(query, sort=search_sort, limit=limit))
        all_results.extend(results)
        logger.info("Found %d results in r/%s", len(results), name)

    logger.info("Total: %d search results", len(all_results))
    return all_results


# ---------------------------------------------------------------------------
# Filtering — structured access to data
# ---------------------------------------------------------------------------


def filter_by_keywords(
    posts: list[praw.models.Submission],
    keywords: list[str],
) -> list[praw.models.Submission]:
    """Filter posts whose title or body contains at least one keyword.

    Narrows down publicly available data so users can focus on
    the discussions most relevant to them.
    """
    if not keywords:
        return posts

    keywords_lower = [kw.lower().strip() for kw in keywords]
    matched = [
        post
        for post in posts
        if any(
            kw in post.title.lower() or kw in (post.selftext or "").lower()
            for kw in keywords_lower
        )
    ]
    logger.info(
        "Keyword filter: %d/%d posts matched keywords %s",
        len(matched),
        len(posts),
        keywords_lower,
    )
    return matched


# ---------------------------------------------------------------------------
# Display — structured and user-friendly presentation
# ---------------------------------------------------------------------------


def _truncate(text: str, max_length: int = BODY_PREVIEW_LENGTH) -> str:
    """Return a truncated preview of the text."""
    if not text:
        return ""
    text = " ".join(text.split())  # collapse whitespace
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + " ..."


def display_posts(posts: list[praw.models.Submission]) -> None:
    """Present discovered discussions in a structured, user-friendly format.

    Displays title, metadata, and a content preview so users can quickly
    assess which discussions are relevant to them.
    """
    if not posts:
        print("\n  No discussions found matching your criteria.\n")
        return

    separator = "-" * 72

    print(f"\n{'=' * 72}")
    print(f" {'DISCOVERED DISCUSSIONS':^70}")
    print(f"{'=' * 72}")
    print(f"  {len(posts)} result(s) found\n")

    for idx, post in enumerate(posts, start=1):
        created = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
        subreddit_label = f"r/{post.subreddit.display_name}"

        print(f"  [{idx}] {post.title}")
        print(f"      Sub    : {subreddit_label}")
        print(f"      Author : u/{post.author}")
        print(f"      Score  : {post.score}  |  Comments: {post.num_comments}")
        print(f"      Date   : {created:%Y-%m-%d %H:%M:%S UTC}")
        print(f"      Link   : https://reddit.com{post.permalink}")

        # Show a body preview when available for extra useful information
        preview = _truncate(post.selftext)
        if preview:
            wrapped = textwrap.fill(
                preview, width=64, initial_indent="      > ", subsequent_indent="        "
            )
            print(wrapped)

        print(f"      {separator}")

    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Discover relevant Reddit discussions and useful information. "
            "This tool provides structured, read-only access to publicly "
            "available data — it does not manipulate content or automate "
            "interactions."
        ),
    )
    parser.add_argument(
        "-s",
        "--subreddits",
        default=",".join(DEFAULT_SUBREDDITS),
        help=(
            "Comma-separated list of subreddits to explore "
            f"(default: {','.join(DEFAULT_SUBREDDITS)})"
        ),
    )
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"Number of posts to fetch per subreddit (default: {DEFAULT_LIMIT})",
    )
    parser.add_argument(
        "-k",
        "--keywords",
        default="",
        help='Comma-separated keywords to filter on (e.g. "async,typing,pep")',
    )
    parser.add_argument(
        "--sort",
        default=DEFAULT_SORT,
        choices=VALID_SORTS,
        help=f"Sort order for browsing (default: {DEFAULT_SORT})",
    )
    parser.add_argument(
        "--search",
        default="",
        help='Search query to discover relevant discussions (e.g. "async python")',
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point — discover discussions in a respectful, read-only manner."""
    args = parse_args()

    subreddit_names = [s.strip() for s in args.subreddits.split(",") if s.strip()]
    keywords = (
        [kw for kw in args.keywords.split(",") if kw.strip()]
        if args.keywords
        else DEFAULT_KEYWORDS
    )

    reddit = get_reddit_client()

    # Choose between search mode and browse mode
    if args.search:
        posts = search_discussions(
            reddit, args.search, subreddit_names, sort=args.sort, limit=args.limit
        )
    else:
        posts = fetch_posts_from_multiple(
            reddit, subreddit_names, sort=args.sort, limit=args.limit
        )

    matched = filter_by_keywords(posts, keywords)
    display_posts(matched)


if __name__ == "__main__":
    main()
