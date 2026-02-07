# Reddit Subreddit Monitor

A minimal, clean Python tool for personal monitoring of Reddit subreddits using the [Reddit Data API](https://www.reddit.com/dev/api/) via [PRAW](https://praw.readthedocs.io/) (Python Reddit API Wrapper).

## Purpose

This project is a **personal monitoring / research tool** designed to:

- Fetch the latest posts from one or more subreddits
- Filter posts by keywords for targeted alerts / watch-lists
- Log and display matching results in the terminal

### What this project is **NOT**

- **Not a commercial product** — strictly for personal use and learning
- **Not a data scraper** — it fetches a small, bounded number of posts per request
- **No mass redistribution of Reddit data** — results are consumed locally

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
   - **name**: `reddit_monitor` (or any name you like)
   - **type**: select **script**
   - **description**: _Personal subreddit monitoring tool_
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
REDDIT_USER_AGENT=reddit_monitor:v1.0.0 (by u/your_reddit_username)
```

> **Important:** Never commit your `.env` file. It is already listed in `.gitignore`.

## Usage

```bash
# Fetch 10 latest posts from r/python (default)
python main.py

# Fetch 20 latest posts from r/machinelearning
python main.py --subreddit machinelearning --limit 20

# Filter posts by keywords
python main.py --subreddit python --keywords "async,typing,pep"
```

### CLI Options

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--subreddit` | `-s` | `python` | Subreddit to monitor |
| `--limit` | `-l` | `10` | Number of recent posts to fetch |
| `--keywords` | `-k` | _(none)_ | Comma-separated keywords to filter on |

## Project Structure

```
reddit_app_helper/
├── main.py            # Main monitoring script
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
