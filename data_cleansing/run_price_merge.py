import psycopg2
import psycopg2.extras
import os
import pandas as pd


def get_db_connection():
    """Establish and return a connection to the database."""
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
    """Extract all data from the specified ODS table and return a Pandas DataFrame."""
    print(f"Extracting data from {table_name}...")
    query = f"SELECT * FROM {table_name};"
    df = pd.read_sql_query(query, connection)
    print(f"Successfully extracted {len(df)} records from {table_name}.")
    return df


def transform_data(reddit_df, gnews_df, newsapi_df):
    """Transform and merge DataFrames from different sources into a unified format."""
    print("Starting data transformation...")
    transformed_posts = []

    # 1. Process Reddit data
    for index, row in reddit_df.iterrows():
        # Reddit typically doesn't have a separate description, so title + content
        title = row['title'] or ''
        content = row['content'] or ''
        # <--- Core modification: merge text fields ---
        full_content = f"{title}\n\n{content}".strip()

        transformed_posts.append({
            'id': f"reddit_{row['id']}",
            'source': 'reddit',
            'title': title,
            'content': full_content,  # <-- Use merged content
            'published_at': row['created_utc'],
            'source_name': row['subreddit'],
            'subreddit': row['subreddit'],
            'url': row['url'],
            'topic': None
        })

    # 2. Process GNews data
    for index, row in gnews_df.iterrows():
        title = row['title'] or ''
        description = row['description'] or ''
        content = row['content'] or ''
        # <--- Core modification: merge text fields ---
        full_content = f"{title}\n\n{description}\n\n{content}".strip()

        transformed_posts.append({
            'id': f"gnews_{row['article_id']}",
            'source': 'gnews',
            'title': title,
            'content': full_content,  # <-- Use merged content
            'published_at': row['published_at'],
            'source_name': row['source_name'],
            'subreddit': None,
            'url': row['url'],
            'topic': None
        })

    # 3. Process NewsAPI data
    for index, row in newsapi_df.iterrows():
        title = row['title'] or ''
        description = row['description'] or ''
        content = row['content'] or ''
        # <--- Core modification: merge text fields ---
        full_content = f"{title}\n\n{description}\n\n{content}".strip()

        transformed_posts.append({
            'id': f"newsapi_{row['id']}",
            'source': 'newsapi',
            'title': title,
            'content': full_content,  # <-- Use merged content
            'published_at': row['published_at'],
            'source_name': row['source_name'],
            'subreddit': None,
            'url': row['url'],
            'topic': None
        })

    print(f"Data transformation complete, generated {len(transformed_posts)} unified records.")
    return pd.DataFrame(transformed_posts)


def load_to_dwd(connection, target_df):
    """Loads the unified DataFrame into the DWD table."""
    if target_df.empty:
        print("No data to load, skipping.")
        return

    table_name = "dwd.media_posts_cleaned"
    print(f"Preparing to load {len(target_df)} records into {table_name}...")

    with connection.cursor() as cur:
        cur.execute(f"TRUNCATE TABLE {table_name};") # Truncate table before loading
        print(f"Target table {table_name} has been truncated.")

    sql = f"""
        INSERT INTO {table_name} (
            id, source, title, content, published_at, source_name, subreddit, url, topic
        ) VALUES %s
        ON CONFLICT (id) DO NOTHING; # Handle conflicts by doing nothing
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
        print("\nMedia data merging task completed successfully!")
    except Exception as e:
        print(f"\nTask execution failed: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")


if __name__ == "__main__":
    main()