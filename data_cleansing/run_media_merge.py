import psycopg2
import psycopg2.extras
import os
import pandas as pd


def get_db_connection():
    """Establishes and returns a connection to the database."""
    try:
        conn = psycopg2.connect(
            host="db",
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD")
        )
        print("Database connection successful!")
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise


def extract_from_ods(connection, table_name):
    """Extracts all data from a specified ODS table and returns it as a Pandas DataFrame."""
    print(f"Extracting data from {table_name}...")
    query = f"SELECT * FROM {table_name};"
    df = pd.read_sql_query(query, connection)
    print(f"Successfully extracted {len(df)} records from {table_name}.")
    return df


def transform_data(reddit_df, gnews_df, newsapi_df):
    """Transforms and merges media data DataFrames from different sources into a unified format."""
    print("Starting data transformation for media...")
    transformed_posts = []

    # 1. Process Reddit data
    for _, row in reddit_df.iterrows():
        title = row.get('title') or ''
        content = row.get('content') or ''
        full_content = f"{title}\n\n{content}".strip()

        transformed_posts.append({
            'id': f"reddit_{row['id']}",
            'source': 'reddit',
            'title': title,
            'content': full_content,
            'published_at': row['created_utc'],
            'source_name': row['subreddit'],
            'subreddit': row['subreddit'],
            'url': row['url'],
            'topic': None
        })

    # 2. Process GNews data
    for _, row in gnews_df.iterrows():
        title = row.get('title') or ''
        description = row.get('description') or ''
        content = row.get('content') or ''
        full_content = f"{title}\n\n{description}\n\n{content}".strip()

        transformed_posts.append({
            'id': f"gnews_{row['article_id']}",
            'source': 'gnews',
            'title': title,
            'content': full_content,
            'published_at': row['published_at'],
            'source_name': row['source_name'],
            'subreddit': None,
            'url': row['url'],
            'topic': None
        })

    # 3. Process NewsAPI data
    for _, row in newsapi_df.iterrows():
        title = row.get('title') or ''
        description = row.get('description') or ''
        content = row.get('content') or ''
        full_content = f"{title}\n\n{description}\n\n{content}".strip()

        transformed_posts.append({
            'id': f"newsapi_{row['id']}",
            'source': 'newsapi',
            'title': title,
            'content': full_content,
            'published_at': row['published_at'],
            'source_name': row['source_name'],
            'subreddit': None,
            'url': row['url'],
            'topic': None
        })

    print(f"Data transformation complete, generated {len(transformed_posts)} unified records.")
    # Convert list of dictionaries to a Pandas DataFrame and specify column order to match the DWD table
    final_df = pd.DataFrame(transformed_posts)
    if final_df.empty:
        return final_df

    dwd_columns_order = [
        'id', 'source', 'title', 'content', 'published_at',
        'source_name', 'subreddit', 'url', 'topic'
    ]
    # We only select columns that actually exist in the DWD table
    # Note: `inserted_at` is generated automatically by the database, we don't need to provide it
    return final_df[dwd_columns_order]


def load_to_dwd(connection, target_df):
    """Loads the unified DataFrame into the dwd.media_posts_cleaned table."""
    if target_df.empty:
        print("No data to load into DWD, skipping.")
        return

    table_name = "dwd.media_posts_cleaned"
    print(f"Preparing to load {len(target_df)} records into {table_name}...")

    with connection.cursor() as cur:
        cur.execute(f"TRUNCATE TABLE {table_name};")
        print(f"Target table {table_name} has been truncated.")

    sql = f"""
        INSERT INTO {table_name} (
            id, source, title, content, published_at, source_name, subreddit, url, topic
        ) VALUES %s
        ON CONFLICT (id) DO NOTHING;
    """

    data_tuples = [tuple(row) for row in target_df.to_numpy()]

    with connection.cursor() as cur:
        psycopg2.extras.execute_values(cur, sql, data_tuples)

    connection.commit()
    print(f"Successfully loaded {len(target_df)} records into {table_name}!")


def main():
    """Main execution function"""
    conn = None
    try:
        conn = get_db_connection()

        reddit_df = extract_from_ods(conn, "ods.media_reddit_posts")
        gnews_df = extract_from_ods(conn, "ods.media_gnews_articles")
        newsapi_df = extract_from_ods(conn, "ods.media_newsapi_articles")

        unified_df = transform_data(reddit_df, gnews_df, newsapi_df)

        load_to_dwd(conn, unified_df)

        print("\nMedia data aggregation task completed successfully!")

    except Exception as e:
        print(f"\nTask execution failed: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")


if __name__ == "__main__":
    main()