# Reddit Discussion Discovery Tool

A simple and respectful tool that helps users discover relevant discussions and useful information more easily. The app does not manipulate content or automate interactions. Instead, it focuses on improving access to publicly available data in a structured and user-friendly way.

Built with [PRAW](https://praw.readthedocs.io/) (Python Reddit API Wrapper) and the [Reddit Data API](https://www.reddit.com/dev/api/).

## Features

- **Discover discussions** — browse or search posts across one or more subreddits
- **Search mode** — find relevant discussions by query (`--search "async python"`)
- **Multi-subreddit** — explore several communities at once (`--subreddits python,learnpython`)
- **Keyword filtering** — narrow results to the most relevant topics
- **Sort options** — hot, new, top, or rising
- **Content preview** — shows a snippet of post body for quick assessment
- **Read-only** — no content manipulation, no automated interactions

### What this project is **NOT**

- **Not a commercial product** — strictly for personal use and learning
- **Not a data scraper** — it fetches a small, bounded number of posts per request
- **No mass redistribution of Reddit data** — results are consumed locally
- **No automated interactions** — no voting, commenting, posting, or messaging

## Responsible Usage

This tool is built and operated in full compliance with:

- [Reddit API Terms of Use](https://www.reddit.com/wiki/api-terms)
- [Reddit's Responsible Builder Policy](https://support.reddithelp.com/hc/en-us/articles/26410290525844-Reddit-Data-API-Wiki)
- PRAW's built-in rate-limit handling (respects Reddit's `X-Ratelimit-*` headers automatically)

The client runs in **read-only mode** and makes minimal API calls.

## Prerequisites

- Python 3.10+
- A Reddit account
- A Reddit API application (see setup below)

## Setup

### 1. Create a Reddit API Application

1. Go to <https://www.reddit.com/prefs/apps>
2. Click **"create another app…"**
3. Fill in the form:
   - **name**: `reddit_discovery` (or any name you like)
   - **type**: select **script**
   - **description**: _Personal discussion discovery tool_
   - **redirect uri**: `http://localhost:8080` (required but unused for script apps)
4. Click **"create app"**
5. Note your **client ID** (the string under the app name) and **client secret**

### 2. Clone & Install

```bash
git clone https://github.com/<your-username>/reddit_app_helper.git
cd reddit_app_helper

python -m venv venv
source venv/bin/activate   # Linux / macOS
# venv\Scripts\activate    # Windows

pip install -r requirements.txt
```

### 3. Configure Credentials

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=reddit_discovery:v1.0.0 (by u/your_reddit_username)
```

> **Important:** Never commit your `.env` file. It is already listed in `.gitignore`.

## Usage

```bash
# Browse hot posts from r/python (default)
python main.py

# Browse multiple subreddits at once
python main.py --subreddits python,learnpython,django --limit 15

# Search for relevant discussions
python main.py --search "async python" --subreddits python

# Filter by keywords with a specific sort order
python main.py --subreddits python --keywords "async,typing,pep" --sort new

# Browse top posts from r/machinelearning
python main.py --subreddits machinelearning --sort top --limit 20
```

### CLI Options

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--subreddits` | `-s` | `python` | Comma-separated subreddits to explore |
| `--limit` | `-l` | `10` | Number of posts per subreddit |
| `--keywords` | `-k` | _(none)_ | Comma-separated keywords to filter on |
| `--sort` | | `hot` | Sort order: `hot`, `new`, `top`, `rising` |
| `--search` | | _(none)_ | Search query to discover relevant discussions |

## Project Structure

```
reddit_app_helper/
├── main.py            # Main discovery tool
├── requirements.txt   # Python dependencies
├── .env.example       # Template for credentials
├── .gitignore         # Git ignore rules
├── LICENSE            # MIT License
└── README.md          # This file
```

## License

This project is licensed under the [MIT License](LICENSE).

## Disclaimer

This tool is provided as-is for educational and personal use. The author is not affiliated with Reddit, Inc. Use responsibly and in accordance with Reddit's terms of service.
