import os
import time
import pandas as pd
import psycopg2
from typing import List, Tuple
from psycopg2.extras import execute_values
import bcrypt

# --------------------------
# DB connection & readiness
# --------------------------
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
    )

def wait_for_postgres(max_retries: int = 30, delay: float = 2.0):
    for attempt in range(1, max_retries + 1):
        try:
            conn = get_db_connection()
            conn.close()
            print("[INFO] PostgreSQL is ready.")
            return
        except psycopg2.OperationalError as e:
            print(f"[WAIT] PostgreSQL not ready (attempt {attempt}/{max_retries}): {e}")
            time.sleep(delay)
    raise RuntimeError("PostgreSQL did not become ready in time.")

# --------------------------
# CSV → table insert helpers
# --------------------------
BASE_DIR = os.path.dirname(__file__)  # /app/db_seed inside container
EXPORTS_DIR = BASE_DIR  # CSV files are in the same dir as seed.py

def do_insert(table_name: str, df: pd.DataFrame, conflict_cols: List[str] = None):
    if df is None or df.empty:
        print(f"[INFO] skip empty dataframe for {table_name}")
        return

    cols = list(df.columns)
    values = [tuple(x) for x in df.to_numpy()]
    col_names = ",".join(cols)

    if conflict_cols:
        conflict_str = ",".join(conflict_cols)
        sql = f"""
            INSERT INTO {table_name} ({col_names})
            VALUES %s
            ON CONFLICT ({conflict_str}) DO NOTHING;
        """
    else:
        sql = f"INSERT INTO {table_name} ({col_names}) VALUES %s;"

    print(f"[INFO] inserting {len(values)} rows into {table_name} (conflict={conflict_cols or []})")
    conn = get_db_connection()
    try:
        with conn, conn.cursor() as cur:
            execute_values(cur, sql, values, page_size=1000)
        print(f"[OK] inserted into {table_name}")
    finally:
        conn.close()

def load_csv(full_path: str) -> pd.DataFrame:
    if not os.path.exists(full_path):
        print(f"[WARN] file not found: {full_path} (skipped)")
        return pd.DataFrame()

    df = pd.read_csv(full_path)
    print(f"[INFO] loaded {os.path.basename(full_path)} rows={len(df)}")

    for col in df.columns:
        low = col.lower()
        if "time" in low or "date" in low:
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)
            except Exception:
                pass
    return df

def has_unique_constraint(table_name: str, columns: list) -> bool:
    """
    Check if given table has a UNIQUE or PRIMARY KEY constraint exactly matching the given columns list.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT conname
                FROM pg_constraint c
                WHERE c.conrelid = %s::regclass
                  AND c.contype IN ('u', 'p') -- unique or primary key
                  AND array(
                      SELECT a.attname
                      FROM unnest(c.conkey) WITH ORDINALITY AS cols(attnum, ord)
                      JOIN pg_attribute a 
                        ON a.attnum = cols.attnum 
                       AND a.attrelid = c.conrelid
                      ORDER BY cols.ord
                  )::text[] = %s::text[];
            """, (table_name, columns))
            return cur.fetchone() is not None
    finally:
        conn.close()



def seed_exports_data():
    file_table_map: List[Tuple[str, str, List[str]]] = [
        ("media_gnews_articles.csv",       "ods.media_gnews_articles",       ["article_id"]),
        ("media_newsapi_articles.csv",     "ods.media_newsapi_articles",     ["id"]),
        ("media_reddit_posts.csv",         "ods.media_reddit_posts",         ["id"]),
        ("price_coingecko_quotes.csv",     "ods.price_coingecko_quotes",     ["coin_id"]),
        ("price_coinmarketcap_quotes.csv", "ods.price_coinmarketcap_quotes", ["symbol", "last_updated"]),
    ]

    for file_name, table_name, conflict_cols in file_table_map:
        full_path = os.path.join(EXPORTS_DIR, file_name)
        print(f"[STEP] processing {file_name} -> {table_name}")
        df = load_csv(full_path)

        if file_name == "price_coingecko_quotes.csv":
            if "last_updated" in df.columns and "last_updated" not in conflict_cols:
                candidate_cols = conflict_cols + ["last_updated"]
                if has_unique_constraint(table_name, candidate_cols):
                    conflict_cols = candidate_cols
                else:
                    print(
                        f"[WARN] No unique constraint on {candidate_cols} in {table_name}, fallback to {conflict_cols}")

        do_insert(table_name, df, conflict_cols)

# --------------------------
# Default users + survey
# --------------------------
def insert_default_users_with_fixed_password():
    DEFAULT_PASSWORD = "123456"
    DEFAULT_USERS = [
        {"email": "default-free@example.com",        "username": "default_free",        "plan": "Free"},
        {"email": "default-pro@example.com",         "username": "default_pro",         "plan": "Pro"},
        {"email": "default-enterprise@example.com",  "username": "default_enterprise",  "plan": "Enterprise"},
    ]

    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT subscription_id, name FROM ods.subscriptions;")
                subs = {name: sid for sid, name in cur.fetchall()}

                for u in DEFAULT_USERS:
                    plan = u["plan"]
                    if plan not in subs:
                        print(f"[WARN] subscription plan not found: {plan}. Skip this user.")
                        continue

                    subscription_id = subs[plan]
                    hashed = bcrypt.hashpw(DEFAULT_PASSWORD.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

                    cur.execute(
                        """
                        INSERT INTO ods.users (username, email, password_hash, created_at, subscription_id)
                        VALUES (%s, %s, %s, NOW(), %s)
                        ON CONFLICT (email) DO UPDATE
                          SET username = EXCLUDED.username,
                              password_hash = EXCLUDED.password_hash,
                              subscription_id = EXCLUDED.subscription_id
                        RETURNING user_id;
                        """,
                        (u["username"], u["email"], hashed, subscription_id),
                    )
                    user_id = cur.fetchone()[0]

                    cur.execute("SELECT 1 FROM ods.survey_results WHERE user_id = %s LIMIT 1;", (user_id,))
                    exists = cur.fetchone() is not None
                    if not exists:
                        cur.execute(
                            """
                            INSERT INTO ods.survey_results (
                                user_id, score, rating,
                                answer_q1, answer_q2, answer_q3,
                                answer_q4, answer_q5, answer_q6, created_at
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW());
                            """,
                            (
                                user_id,
                                75, "B-Level - Balanced",
                                "intermediate 10",
                                "invest 20",
                                "sentiment 10",
                                "daily 20",
                                "no 10",
                                "noise 5",
                            ),
                        )

        print("[OK] default users & survey results inserted/updated.")
        print("Login accounts (password for all: 123456):")
        for u in DEFAULT_USERS:
            print(f"  {u['email']} / 123456 ({u['plan']})")
    finally:
        conn.close()

# --------------------------
# Main
# --------------------------
if __name__ == "__main__":
    wait_for_postgres()
    insert_default_users_with_fixed_password()
    seed_exports_data()
    print("[DONE] seed completed.")
