"""
Overwrites a target table with the contents of a DataFrame.

"""

import os
import psycopg2
import pandas as pd
import random
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import time
from predict import predict_trend
import numpy as np
from predict_aml import aml_predict


table_columns = {
    "dws.price_tb": ["symbol", "price", "last_updated"],
    "dws.statistic_tb": [
        "symbol", "volume_24h", "percent_change_24h", "percent_change_7d",
        "market_cap", "circulating_supply", "total_supply", "max_supply", "last_updated"
    ],
    "dws.content_sa_tb": [
        "symbol", "title", "content", "sentiment", "sentiment_score", "url"
    ],
    "dws.aml_tb": ["symbol", "title", "aml"],
    "dws.latest_news": ["symbol", "title", "url"],
    "dws.predict_res": ['time', 'symbol', 'trend'],
    "dws.aml_predictions": ['time', 'symbol', 'amount', 'aml_label']
}


def wait_for_postgres(max_retries=10, delay=2):
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                host="db",
                dbname=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                port=5432
            )
            conn.close()
            print(" PostgreSQL is ready.")
            return
        except psycopg2.OperationalError:
            print(f" Waiting for PostgreSQL... (attempt {attempt + 1})")
            time.sleep(delay)
    raise RuntimeError("PostgreSQL did not become ready in time.")


def get_conn():
    return psycopg2.connect(
        host="db",
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )


def write_df_to_table(df, table_name, conn, columns):
    df_columns = [col for col in columns if col in df.columns]
    with conn.cursor() as cur:
        placeholders = ', '.join(['%s'] * len(df_columns))
        cols = ', '.join(df_columns)
        insert_sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
        cur.executemany(insert_sql, df[df_columns].values.tolist())
    conn.commit()


def load_table(query, conn):
    return pd.read_sql(query, conn)


def overwrite_table(df, table_name, conn):
    with conn.cursor() as cur:
        cur.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY;")
        print(f"Table {table_name} truncated.")
    conn.commit()
    columns = table_columns[table_name]
    write_df_to_table(df, table_name, conn, columns)
    print(f" Overwrote {len(df)} rows into {table_name}")

if __name__ == "__main__":
    wait_for_postgres()
    print('\n', '-- Analysis --')
    conn = get_conn()

    
    d = load_table("SELECT symbol, title, content, url FROM dwd.social_media_agg", conn=conn)
    d['symbol'] = d['symbol'].str.lower()

    # write price data
    price_df = load_table("SELECT symbol, price, time AS last_updated FROM dwd.price_assets_agg", conn=conn)
    price_df['symbol'] = price_df['symbol'].str.lower()
    overwrite_table(price_df, "dws.price_tb", conn)


    cmark_stats = load_table(
        "SELECT symbol, volume_24h, percent_change_24h, percent_change_7d, market_cap,"
        " circulating_supply, total_supply, max_supply, last_updated FROM ods.price_coinmarketcap_quotes",
        conn=conn)


    statistic_tb = cmark_stats.sort_values('last_updated', ascending=False).drop_duplicates('symbol')

    analyzer = SentimentIntensityAnalyzer()

    # --- Trend Prediction Feature Engineering ---
    # The following section prepares the input data for the trend prediction model.
    # It loads recent social media data, performs sentiment analysis, and pivots
    # the data into a feature matrix where each row represents a symbol at a
    # specific hour, and columns represent sentiment from different sources.

    media_tb = load_table("""
        SELECT symbol, title, content, time AS time, source
        FROM dwd.social_media_agg
    """, conn=conn)

    media_tb['sentiment'] = media_tb['title'].apply(
        lambda t: analyzer.polarity_scores(str(t))['compound'] if isinstance(t, str) else np.nan
    )

    def classify_sentiment(score):
        if pd.isna(score):
            return 'no_data'
        elif score < -0.6:
            return 'neg_strong'
        elif score < -0.2:
            return 'neg_weak'
        elif score <= 0.2:
            return 'neutral'
        elif score <= 0.6:
            return 'pos_weak'
        elif score <= 1:
            return 'pos_strong'
        else:
            return 'no_data'

    media_tb['sentiment_class'] = media_tb['sentiment'].apply(classify_sentiment)

    media_tb['time'] = pd.to_datetime(media_tb['time']).dt.floor('h')

    # This chain of pandas operations transforms the data:
    # 1. groupby: Group by time, symbol, and source.
    # 2. agg: Find the most frequent sentiment class within each group.
    # 3. unstack: Pivot the 'source' index level into columns.
    # The result is a table ready for prediction.

    media_agg = media_tb.groupby(['time', 'symbol', 'source'])['sentiment_class'].agg(
        lambda x: x.value_counts().idxmax()).unstack('source')
    all_sources = ['banknews', 'gnews', 'newsapi', 'reddit', 'youtube']
    media_agg = media_agg.reindex(columns=all_sources, fill_value='no_data')
    media_agg = media_agg.reset_index()
    media_agg = media_agg.fillna('no_data')

    print('media_add keys:', media_agg.keys())
    print('TRYING MEDIA_AGG:\n', media_agg)
    if media_agg.empty:
        print("media_agg is empty, skipping trend prediction.")
        media_agg['trend'] = ['stable'] * len(media_agg)
    else:
        media_agg['trend'] = media_agg.apply(
            lambda row: predict_trend({src: row[src] for src in all_sources}),
            axis=1
        )
    print('media_add keys:', media_agg.keys())
    print('TRYING MEDIA_AGG:\n', media_agg)
    media_agg = media_agg[['time', 'symbol', 'trend']]
    media_agg['symbol'] = media_agg['symbol'].str.lower()

    overwrite_table(media_agg, "dws.predict_res", conn)

    def analyze_sentiment(row):
        text = row.get("content", "")
        if not isinstance(text, str) or not text.strip():
            text = row.get("title", "")
        if not isinstance(text, str) or not text.strip():
            return {"sentiment": "neutral", "score": 0.0}

        score = analyzer.polarity_scores(text)["compound"]
        sentiment = (
            "positive" if score >= 0.05 else
            "negative" if score <= -0.05 else
            "neutral"
        )
        return {"sentiment": sentiment, "score": score}

    def random_aml_risk():
        return "Safe" if random.random() < 0.8 else "There is a possibility of money laundering."


    d_sampled = d[['symbol', 'title']].groupby('symbol').head(2).reset_index(drop=True)

    all_symbols = statistic_tb['symbol'].unique()

    aml_tb_base = pd.DataFrame({
        'symbol': all_symbols,
        'aml': [random_aml_risk() for _ in range(len(all_symbols))]
    })

    aml_tb = pd.merge(d_sampled, aml_tb_base, on='symbol', how='right')
    aml_tb['title'] = aml_tb['title'].fillna('No specific article flagged.')  # Fill in missing headers

    news = load_table("SELECT symbol, title, content, url FROM dwd.social_media_agg", conn=conn)
    news_ = news[['symbol', 'title', 'url']]
    print('[DEBUG news table]', news.head())

    sentiment_results = news.apply(analyze_sentiment, axis=1)
    d["sentiment"] = sentiment_results.apply(lambda x: x["sentiment"])
    d["sentiment_score"] = sentiment_results.apply(lambda x: x["score"])

    sentiment_tb = d[['symbol', 'title', 'content', 'sentiment', 'sentiment_score', 'url']]

    print('[DEBUG sentiment tb]', sentiment_tb.head())

    # Perform write operation
    
    aml_tb = aml_predict()

    overwrite_table(aml_tb, "dws.aml_predictions", conn)
    overwrite_table(statistic_tb, "dws.statistic_tb", conn)
    overwrite_table(sentiment_tb, "dws.content_sa_tb", conn)
    overwrite_table(aml_tb, "dws.aml_tb", conn)
    overwrite_table(news_, "dws.latest_news", conn)

    print('-- Analysis finished --', '\n')
    conn.close()