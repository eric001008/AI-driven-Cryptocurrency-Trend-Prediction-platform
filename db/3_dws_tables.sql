CREATE SCHEMA IF NOT EXISTS dws;

CREATE TABLE IF NOT EXISTS dws.price_tb (
    symbol TEXT,
    price NUMERIC,
    last_updated TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS dws.statistic_tb (
    symbol TEXT,
    volume_24h NUMERIC,
    percent_change_24h REAL,
    percent_change_7d REAL,
    market_cap NUMERIC,
    circulating_supply NUMERIC,
    total_supply NUMERIC,
    max_supply NUMERIC,
    last_updated TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS dws.content_sa_tb (
    symbol TEXT,
    title TEXT,
    content TEXT,
    sentiment TEXT,             -- 'positive', 'neutral', 'negative'
    sentiment_score REAL,       -- [-1.0, 1.0]
    url TEXT
);

CREATE TABLE IF NOT EXISTS dws.aml_tb (
    symbol TEXT,                                             -- Token symbol, e.g. 'BTC'
    title TEXT,                                              -- Related news headlines
    url TEXT,                                                -- News Links
    aml TEXT
);

CREATE TABLE IF NOT EXISTS dws.latest_news (
    symbol TEXT,                                             
    title TEXT,                                              
    url TEXT                                                
);
 
CREATE INDEX IF NOT EXISTS idx_price_symbol ON dws.price_tb(symbol);
CREATE INDEX IF NOT EXISTS idx_sentiment_symbol ON dws.content_sa_tb(symbol);


CREATE TABLE IF NOT EXISTS dws.predict_res (
    time        TIMESTAMPTZ       NOT NULL,
    symbol      TEXT              NOT NULL,
    trend       TEXT              NOT NULL
);


CREATE TABLE dws.aml_predictions ( 
    symbol TEXT NOT NULL,            -- Cryptocurrency symbol (e.g., BTC, ETH)
    amount DOUBLE PRECISION,           -- Transaction amount in USDT equivalent
    aml_label SMALLINT                 -- AML risk label: 1 = suspicious, 0 = normal
);
