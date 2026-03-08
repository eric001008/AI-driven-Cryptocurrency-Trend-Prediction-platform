import os
import psycopg2
import pandas as pd
import random
from psycopg2.extras import execute_values
import time


def wait_for_postgres(max_retries=10, delay=2):
    """
    Waits for the PostgreSQL database to become available.

    This is a utility function designed for Docker environments where the
    application container might start faster than the database container.
    It attempts to connect multiple times before giving up.
    """
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
            print("PostgreSQL is ready.")
            return
        except psycopg2.OperationalError:
            print(f"Waiting for PostgreSQL... (attempt {attempt + 1})")
            time.sleep(delay)
    raise RuntimeError("PostgreSQL did not become ready in time.")


def get_db_connection():
    """Establishes and returns a new database connection."""
    conn = psycopg2.connect(
        host="db",
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
    return conn


def extract_from_ods(connection, table_name):
    """Extracts all data from a specified ODS table into a pandas DataFrame."""
    query = f"SELECT * FROM {table_name};"
    try:
        df = pd.read_sql_query(query, connection)
        if df.empty:
            print(f"[DEBUG CLEANSING] No data found in table: {table_name}")
        else:
            print('[DEBUG CLEANSING] get {l} cols of data from {table_name}'.format(l=len(df), table_name=table_name))
        return df
    except Exception as e:
        print(f"[DEBUG CLEANSING] Failed to extract from {table_name}: {e}")
        return pd.DataFrame()


# Set a seed for random operations to ensure reproducibility.
random.seed(42)

# --- Configuration: Mapping of data sources to their table names ---
ods_media_map = {
    "reddit": "ods.media_reddit_posts",
    "gnews": "ods.media_gnews_articles",
    "newsapi": "ods.media_newsapi_articles",
    "youtube": "ods.media_youtube_videos",
    "banknews": "ods.media_banknews_articles"
}

ods_coin_map = {
    "coingecko": "ods.price_coingecko_quotes",
    "coinmarketcap": "ods.price_coinmarketcap_quotes"
}

# --- Configuration: Target DWD (Data Warehouse Detail) table names ---
dwd_price_table = "dwd.price_assets_agg"
dwd_statistic_coin = "dwd.coin_statistic"
dwd_social_media = "dwd.social_media_agg"


def transform_media_tables(media_dfs: dict) -> pd.DataFrame:

    # Normalizes and combines DataFrames from various media sources into a single DataFrame.

    transformed = []

    # Standardize Reddit data
    if "reddit" in media_dfs and not media_dfs["reddit"].empty:
        df = media_dfs["reddit"]
        transformed.append(pd.DataFrame({
            "source": "reddit",
            "title": df["title"],
            "content": df["content"],
            "time": df["created_utc"],
            "url": df["url"]
        }))

    # Standardize GNews data
    if "gnews" in media_dfs and not media_dfs["gnews"].empty:
        df = media_dfs["gnews"]
        transformed.append(pd.DataFrame({
            "source": "gnews",
            "title": df["title"],
            "content": df["description"].fillna(""),  # Ensure content is never null
            "time": df["published_at"],
            "url": df["url"]
        }))

    # Standardize NewsAPI data
    if "newsapi" in media_dfs and not media_dfs["newsapi"].empty:
        df = media_dfs["newsapi"]
        transformed.append(pd.DataFrame({
            "source": "newsapi",
            "title": df["title"],
            "content": df["description"].fillna(""),
            "time": df["published_at"],
            "url": df["url"]
        }))

    # Standardize YouTube data
    if "youtube" in media_dfs and not media_dfs["youtube"].empty:
        df = media_dfs["youtube"]
        transformed.append(pd.DataFrame({
            "source": "youtube",
            "title": df["title"],
            "content": df["description"].fillna(""),
            "time": df["published_at"],
            "url": df["url"]
        }))

    # Standardize BankNews data
    if "banknews" in media_dfs and not media_dfs["banknews"].empty:
        df = media_dfs["banknews"]
        transformed.append(pd.DataFrame({
            "source": "banknews",
            "title": df["title"],
            "content": df["content"],
            "time": df["published_at"],
            "url": df["url"]
        }))

    # # Standardize Telegram data
    # if "telegram" in media_dfs and not media_dfs["telegram"].empty:
    #     df = media_dfs["telegram"]
    #     transformed.append(pd.DataFrame({
    #         "source": "telegram",
    #         "title": df["content"].str.slice(0, 50),  # Use first 50 chars of content as title
    #         "content": df["content"],
    #         "time": df["sent_at"],
    #         "url": df["url"]
    #     }))

    # Combine all transformed DataFrames into one
    if transformed:
        return pd.concat(transformed, ignore_index=True)[["source", "title", "content", "url", "time"]]
    else:
        return pd.DataFrame(columns=["source", "title", "content", "url", "time"])


def write_df_to_table(df, table_name, conn, columns, on_conflict_fields=None):
    """
    Writes a DataFrame to a database table, with high-performance bulk insertion.

    If `on_conflict_fields` is provided, it uses `execute_values` with an
    `ON CONFLICT DO NOTHING` clause to efficiently handle duplicates.
    """
    with conn.cursor() as cur:
        if on_conflict_fields:
            # Use execute_values for better performance on bulk inserts with conflict handling
            insert_sql = f"""
                INSERT INTO {table_name} ({', '.join(columns)})
                VALUES %s
                ON CONFLICT ({', '.join(on_conflict_fields)}) DO NOTHING
            """
            execute_values(cur, insert_sql, df[columns].values.tolist())
        else:
            # Fallback for simple inserts without conflict handling
            placeholders = ', '.join(['%s'] * len(columns))
            insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            cur.executemany(insert_sql, df[columns].values.tolist())

    conn.commit()


if __name__ == "__main__":
    wait_for_postgres()
    print("aggregation!!")
    conn = get_db_connection()

    # combine price table
    coingecko_df = extract_from_ods(conn, "ods.price_coingecko_quotes")
    coinmarketcap_df = extract_from_ods(conn, "ods.price_coinmarketcap_quotes")

    if not coingecko_df.empty:
        coingecko_df = coingecko_df.rename(columns={
            "current_price": "price",
            "last_updated": "time"
        })[["symbol", "price", "time"]]

    if not coinmarketcap_df.empty:
        coinmarketcap_df = coinmarketcap_df.rename(columns={
            "last_updated": "time"
        })[["symbol", "price", "time"]]

    combined_price_df = pd.concat([coingecko_df, coinmarketcap_df], ignore_index=True)
    combined_price_df = combined_price_df.drop_duplicates(subset=["symbol", "time"])

    # combine social media table
    media_dfs = {}

    for key, table in ods_media_map.items():
        try:
            df = extract_from_ods(conn, table)
            media_dfs[key] = df
            print(f"Loaded {len(df)} rows from {table}")
        except Exception as e:
            print(f"Failed to load {table}: {e}")
            media_dfs[key] = pd.DataFrame()
    
    all_symbols = combined_price_df["symbol"].dropna().unique().tolist()

    def match_symbol2content(title, content):

        if not isinstance(title, str):
            title = ""
        if not isinstance(content, str):
            content = ""

        title_lower = title.lower()
        content_lower = content.lower()

        for symbol in all_symbols:
            if symbol.lower() in title_lower:
                return symbol  
            if 'bitcoin' in title_lower:
                return 'BTC'

        for symbol in all_symbols:
            if symbol.lower() in content_lower:
                return symbol  
            if 'bitcoin' in content_lower:
                return 'BTC'

        # return random.choice(all_symbols)
        return 'USDT'


    media_agg = transform_media_tables(media_dfs)
    media_agg["symbol"] = media_agg.apply(
        lambda row: match_symbol2content(row["title"], row["content"]),
        axis=1
    )

    print('len media:', len(media_agg))
    print('len coin:', len(combined_price_df))

    # write
    if not media_agg.empty:
        write_df_to_table(
            df=media_agg,
            table_name=dwd_social_media,
            conn=conn,
            columns=["source", "symbol", "title", "content", "url", "time"],
            on_conflict_fields=["source", "symbol", "title", "time"]
        )
    if not combined_price_df.empty:
        write_df_to_table(
            df=combined_price_df,
            table_name=dwd_price_table,
            conn=conn,
            columns=["symbol", "price", "time"],
            on_conflict_fields=["symbol", "time"]
        )

    conn.close()
    print("Connection closed.")
    print("aggregation finished!!")