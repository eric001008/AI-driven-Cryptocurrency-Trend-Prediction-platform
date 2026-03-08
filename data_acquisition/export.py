import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from a .env file for local development.
load_dotenv("/app/.env")  # If not running in a container, you can change it to ".env"

# Database connection information
conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB", "overdb"),
    user=os.getenv("POSTGRES_USER", "admincedric"),
    password=os.getenv("POSTGRES_PASSWORD", "your_password"),
    host=os.getenv("POSTGRES_HOST", "db"),  
    port=os.getenv("POSTGRES_PORT", 5432)
)


tables = {
    "media_reddit_posts":     "ods.media_reddit_posts",
    "media_gnews_articles":   "ods.media_gnews_articles",
    "media_newsapi_articles": "ods.media_newsapi_articles",
    "price_coingecko_quotes": "ods.price_coingecko_quotes",
    "price_coinmarketcap_quotes": "ods.price_coinmarketcap_quotes"
}

export_dir = "./exports"
os.makedirs(export_dir, exist_ok=True)

# Export each table to CSV
for name, full_table in tables.items():
    print(f"Exporting {full_table}...")
    df = pd.read_sql_query(f"SELECT * FROM {full_table}", conn)
    csv_path = os.path.join(export_dir, f"{name}.csv")
    df.to_csv(csv_path, index=False)
    print(f"Saved to {csv_path}")

conn.close()
print("All tables exported.")
