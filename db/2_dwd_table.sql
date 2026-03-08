CREATE SCHEMA IF NOT EXISTS dwd;

CREATE TABLE IF NOT EXISTS dwd.price_assets_agg (
    symbol TEXT NOT NULL,
    price NUMERIC NOT NULL,
    time TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (symbol, time)
);

CREATE INDEX IF NOT EXISTS idx_price_time ON dwd.price_assets_agg (time DESC);

CREATE INDEX IF NOT EXISTS idx_price_symbol ON dwd.price_assets_agg (symbol);

CREATE TABLE IF NOT EXISTS dwd.social_media_agg (
    source TEXT NOT NULL,
    symbol TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    url TEXT,        
    time TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (source, symbol, title, time)
);

CREATE INDEX IF NOT EXISTS idx_social_time ON dwd.social_media_agg (time DESC);

CREATE INDEX IF NOT EXISTS idx_social_symbol ON dwd.social_media_agg (symbol);


-- fixed
CREATE TABLE dwd.coin_trend_features_tb (
    time_period TIMESTAMPTZ NOT NULL,  -- The UTC time field indicates the start time of the current time period and the time range of 1 hour in the future
    symbol TEXT NOT NULL,

    reddit TEXT,                       -- Sentiment labels, such as pos_strong
    youtube TEXT,
    banknews TEXT,
    gnews TEXT,
    newsapi TEXT,
    telegram TEXT,

    price_trend TEXT                   -- label, target classification variable
);
ALTER TABLE dwd.coin_trend_features_tb
ADD PRIMARY KEY (time_period, symbol);