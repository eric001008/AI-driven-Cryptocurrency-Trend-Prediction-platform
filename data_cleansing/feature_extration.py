import os
import psycopg2
import pandas as pd
from datetime import datetime, timedelta, timezone
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from psycopg2.extras import execute_values


# --- Database Connection ---

def get_db_connection():
    """Establishes and returns a new database connection."""
    return psycopg2.connect(
        host="db",
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )


# --- Data Extraction and Processing Functions ---

def extract_recent_data(conn, table_name, time_column="time", window_minutes=60):
    """
    Extracts data from a specified table within a recent time window.
    """
    now = datetime.utcnow()
    start_time = now - timedelta(minutes=window_minutes)

    query = f"""
        SELECT * FROM {table_name}
        WHERE {time_column} >= %s AND {time_column} <= %s
    """
    # Use params to safely pass timestamps to the query
    df = pd.read_sql_query(query, conn, params=(start_time, now))
    print(f"Loaded {len(df)} rows from {table_name} in the last {window_minutes} minutes")
    return df


def compute_sentiment(media_df, current_period):
    """
    Calculates sentiment scores for media data using VADER.
    It computes a weighted average score based on the sentiment of the title and content.
    """
    analyzer = SentimentIntensityAnalyzer()

    # Drop rows where key text fields are missing
    media_df = media_df.dropna(subset=["title", "content", "symbol", "source"])
    if media_df.empty:
        print("No media data to process for sentiment.")
        return pd.DataFrame(columns=["symbol", "source", "weighted_score", "time_period"])

    # Calculate sentiment score for title and content separately
    media_df["title_score"] = media_df["title"].apply(
        lambda x: analyzer.polarity_scores(x)["compound"]
    )
    media_df["content_score"] = media_df["content"].apply(
        lambda x: analyzer.polarity_scores(x)["compound"]
    )

    # Define weights for title and content scores
    title_weight = 0.5
    content_weight = 0.5

    # Calculate the final weighted score
    media_df["weighted_score"] = (
            media_df["title_score"] * title_weight + media_df["content_score"] * content_weight
    )

    # Tag each row with the current time period for aggregation
    media_df["time_period"] = current_period

    return media_df[["symbol", "source", "weighted_score", "time_period"]]


def classify_price_trends(price_df, current_period):
    """
    Classifies price movement into 'uptrend', 'downtrend', or 'remain'.
    The trend is determined by comparing the first and last price within the
    provided DataFrame for each symbol.
    """
    if price_df.empty:
        return pd.DataFrame(columns=["symbol", "price_trend", "time_period"])

    price_df["time"] = pd.to_datetime(price_df["time"])

    # Group by symbol to find the start and end price in the window
    trend_df = (
        price_df.sort_values(by="time")
            .groupby("symbol")
            .agg(
            start_price=("price", lambda x: x.iloc[0]),
            end_price=("price", lambda x: x.iloc[-1])
        )
            .reset_index()
    )

    def get_trend(row):
        # Define the trend based on the relative change between start and end price
        diff_ratio = abs(row["end_price"] - row["start_price"]) / row["start_price"]
        # If change is less than 0.01%, consider it as 'remain'
        if diff_ratio < 0.0001:
            return "remain"
        elif row["end_price"] > row["start_price"]:
            return "uptrend"
        else:
            return "downtrend"

    trend_df["trend"] = trend_df.apply(get_trend, axis=1)
    trend_df["time_period"] = current_period

    return trend_df[["symbol", "trend", "time_period"]]


def pivot_sentiment_by_source(sentiment_df, current_period):
    """
    Pivots the sentiment data to create a feature matrix.

    """
    if sentiment_df.empty:
        return pd.DataFrame(
            columns=["symbol", "time_period", "reddit", "youtube", "gnews", "newsapi", "banknews", "telegram"])

    sentiment_df["time_period"] = current_period

    # First, group by symbol, source, and time to get the average sentiment
    grouped = sentiment_df.groupby(["symbol", "source", "time_period"]).agg(
        avg_sentiment=("weighted_score", "mean")
    ).reset_index()

    # Convert the numeric average sentiment into a categorical label
    grouped["sentiment_label"] = grouped["avg_sentiment"].apply(score_to_label)

    # Pivot the table to create columns for each source
    pivot = grouped.pivot_table(
        index=["symbol", "time_period"],
        columns="source",
        values="sentiment_label",
        fill_value="no_data",
        aggfunc=lambda x: x.iloc[0]  # Use first value if duplicates exist
    ).reset_index()

    pivot.columns.name = None  # Clean up column axis name

    # Ensure all potential source columns exist, even if there's no data for them
    for col in ["reddit", "youtube", "gnews", "newsapi", "banknews", "telegram"]:
        if col not in pivot.columns:
            pivot[col] = 'no_data'

    return pivot[["symbol", "time_period", "reddit", "youtube", "gnews", "newsapi", "banknews", "telegram"]]


def write_features_to_dwd(df, conn, table_name="dwd.coin_trend_features_tb"):
    """
    Writes the final feature DataFrame to the database using an UPSERT operation.

    """
    cols = ["time_period", "symbol", "reddit", "youtube", "gnews", "newsapi", "banknews", "telegram", "price_trend"]
    with conn.cursor() as cur:
        # Use execute_values for high-performance bulk upserting
        insert_sql = f"""
            INSERT INTO {table_name} ({', '.join(cols)})
            VALUES %s
            ON CONFLICT (time_period, symbol) DO UPDATE SET
                reddit = EXCLUDED.reddit,
                youtube = EXCLUDED.youtube,
                gnews = EXCLUDED.gnews,
                newsapi = EXCLUDED.newsapi,
                banknews = EXCLUDED.banknews,
                telegram = EXCLUDED.telegram,
                price_trend = EXCLUDED.price_trend;
        """
        execute_values(cur, insert_sql, df[cols].values.tolist())

    conn.commit()
    print(f"Inserted/Updated {len(df)} rows into {table_name}")


def score_to_label(score):
    """Converts a continuous sentiment score into a discrete category label."""
    if pd.isna(score):
        return "no_data"
    elif score <= -0.6:
        return "neg_strong"
    elif score <= -0.2:
        return "neg_weak"
    elif score <= 0.2:
        return "neutral"
    elif score <= 0.6:
        return "pos_weak"
    else:
        return "pos_strong"


def main():
    """Main ETL pipeline for feature engineering."""
    conn = get_db_connection()

    # Define the current time window for this run (start of the current hour)
    current_period = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)

    # --- Step 1: Extract recent data from DWD layer ---
    price_df = extract_recent_data(conn, "dwd.price_assets_agg", time_column="time", window_minutes=60)
    media_df = extract_recent_data(conn, "dwd.social_media_agg", time_column="time", window_minutes=60)

    print('get price len:', len(price_df))
    print('get media len:', len(media_df))

    # --- Step 2: Compute features from the raw data ---
    sentiment_summary = compute_sentiment(media_df, current_period)
    sent_by_source = pivot_sentiment_by_source(sentiment_summary, current_period)
    price_trend_summary = classify_price_trends(price_df, current_period)

    # --- Step 3: Merge features into a single table ---
    merged = pd.merge(
        price_trend_summary,
        sent_by_source,
        on=["symbol", "time_period"],
        how="left"  # Use a left join to keep all symbols with a price trend
    )

    # Fill any missing sentiment data with 'no_data' after the merge
    for col in ["reddit", "youtube", "gnews", "newsapi", "banknews", "telegram"]:
        merged[col] = merged[col].fillna("no_data")

    merged = merged.rename(columns={"trend": "price_trend"})
    print('MERGED:::')
    print(merged.keys())
    print(merged.head())

    # --- Step 4: Write final features to the database ---
    write_features_to_dwd(merged, conn, table_name="dwd.coin_trend_features_tb")

    conn.close()
    print("Connection closed.")


if __name__ == "__main__":
    main()