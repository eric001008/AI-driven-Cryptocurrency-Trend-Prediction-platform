CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE SCHEMA IF NOT EXISTS ods;

-- Reddit crypto posts
CREATE TABLE IF NOT EXISTS ods.media_reddit_posts (
    id TEXT PRIMARY KEY,                    -- Reddit post ID (base36)
    title TEXT,                             -- Post title
    content TEXT,                           -- Post body or selftext
    author TEXT,                            -- Username of the poster
    subreddit TEXT,                         -- Subreddit name (e.g., r/Bitcoin)
    created_utc TIMESTAMPTZ NOT NULL,       -- Creation time in UTC
    score INTEGER,                          -- Post score (upvotes - downvotes)
    upvote_ratio REAL,                      -- Ratio of upvotes to total votes
    num_comments INTEGER,                   -- Total number of comments
    url TEXT,                               -- Full URL to the post
    permalink TEXT                          -- Reddit permalink (relative URL)
);

-- GNews crypto articles
CREATE TABLE IF NOT EXISTS ods.media_gnews_articles (
    -- Core change: Use article_id as the primary key and set its data type to TEXT
    article_id TEXT PRIMARY KEY,

    title TEXT,
    description TEXT,                       -- Retain this column, allow nulls even if not provided by the current INSERT
    content TEXT,
    url TEXT,                               -- The original CREATE statement was missing a UNIQUE constraint, which is recommended. Temporarily omitted here to match INSERT logic.
    image_url TEXT,                         -- Retain this column, allow nulls
    published_at TIMESTAMPTZ NOT NULL,
    source_name TEXT,
    source_url TEXT                         -- Retain this column, allow nulls
);

-- NewsAPI crypto articles
CREATE TABLE IF NOT EXISTS ods.media_newsapi_articles (
    id SERIAL PRIMARY KEY,
    title TEXT,                             -- Article title
    description TEXT,                       -- Article description or lead
    content TEXT,                           -- Full article content
    url TEXT UNIQUE,
    image_url TEXT,                         -- URL to article image
    published_at TIMESTAMPTZ NOT NULL,      -- Publication timestamp
    source_name TEXT,                       -- Source name (e.g., CNBC)
    source_url TEXT                         -- Source URL or domain
);

-- CoinGecko price quotes
CREATE TABLE IF NOT EXISTS ods.price_coingecko_quotes (
    -- Core change: Rename the primary key column from 'id' to 'coin_id'
    coin_id TEXT PRIMARY KEY,                 -- CoinGecko coin ID (e.g., 'bitcoin')

    -- Other column definitions remain unchanged as they are correct
    name TEXT,                                -- Full name of the coin (e.g., Bitcoin)
    symbol TEXT,                              -- Ticker symbol (e.g., BTC)
    current_price NUMERIC,                    -- Latest price in specified fiat currency
    market_cap NUMERIC,                       -- Market capitalization
    total_volume NUMERIC,                     -- 24-hour trading volume
    circulating_supply NUMERIC,               -- Currently circulating supply
    total_supply NUMERIC,                     -- Maximum or reported total supply
    last_updated TIMESTAMPTZ NOT NULL         -- Timestamp of the last update from API
);


-- CoinMarketCap market quotes
CREATE TABLE IF NOT EXISTS ods.price_coinmarketcap_quotes (
    -- Includes all columns used in the INSERT statements
    symbol TEXT,
    name TEXT,
    slug TEXT,
    price NUMERIC,
    volume_24h NUMERIC,
    percent_change_1h NUMERIC,
    percent_change_24h NUMERIC,
    percent_change_7d NUMERIC,
    market_cap NUMERIC,
    circulating_supply NUMERIC,
    total_supply NUMERIC,
    max_supply NUMERIC,
    last_updated TIMESTAMPTZ,

    -- Core change: Create a composite primary key to match the ON CONFLICT requirement
    PRIMARY KEY (symbol, last_updated)
);


CREATE TABLE IF NOT EXISTS ods.media_youtube_videos (
    video_id TEXT PRIMARY KEY,              -- YouTube video ID, e.g., 'dQw4w9WgXcQ'
    title TEXT,                             -- Video title
    description TEXT,                       -- Video description
    channel_title TEXT,                     -- Name of the channel that published the video
    published_at TIMESTAMPTZ NOT NULL,      -- Publication time (UTC)
    keyword TEXT,                           -- Keyword used for fetching
    url TEXT                                -- Video link, e.g., 'https://www.youtube.com/watch?v=...'
);


CREATE TABLE IF NOT EXISTS ods.media_banknews_articles (
    article_id TEXT PRIMARY KEY,            -- Custom or hash-generated unique article ID
    title TEXT,                             -- News title
    content TEXT,                           -- News content
    published_at TIMESTAMPTZ NOT NULL,      -- Publication time (UTC)
    url TEXT,                               -- Original link to the news article
    source_name TEXT,                       -- Source website name (e.g., CNBC, Bloomberg)
    keyword TEXT                            -- Keyword used for fetching, e.g., 'crypto bank'
);


-- Create the base table
CREATE TABLE ods.bitquery_records  (
    time TIME NOT NULL,       -- Timestamp column required by TimescaleDB
    date DATE,                       -- Optional separate date column
    sender TEXT,                     -- Sender address
    receiver TEXT,                   -- Receiver address
    amount NUMERIC,                  -- Transaction amount (use NUMERIC for precision)
    currency TEXT
);
