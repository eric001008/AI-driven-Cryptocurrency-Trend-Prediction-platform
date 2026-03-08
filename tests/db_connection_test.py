import os
import pytest
from dotenv import load_dotenv
import psycopg2

load_dotenv(dotenv_path=".env.test") 

def test_database_connection():
    conn = psycopg2.connect(
        host="localhost",
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    assert cur.fetchone()[0] == 1
    cur.close()
    conn.close()
