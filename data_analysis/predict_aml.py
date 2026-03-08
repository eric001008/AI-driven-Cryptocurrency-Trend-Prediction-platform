import pandas as pd
import numpy as np
import random
import string
import networkx as nx
import psycopg2
import os
from datetime import datetime, timedelta, timezone


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


def predict(df_tx, df_price):
    labels = [0] * len(df_tx)
    price_dict = dict(zip(df_price['symbol'], df_price['price']))

    
    df_tx['usdt_equivalent'] = df_tx.apply(
        lambda row: row['amount'] * price_dict.get(row['symbol'], 0),
        axis=1
    )

    for i, val in enumerate(df_tx['usdt_equivalent']):
        if val >= 10000000:
            labels[i] = 1

    df_for_graph = df_tx[df_tx['usdt_equivalent'] >= 100000]

    G = nx.DiGraph()
    for idx, row in df_for_graph.iterrows():
        G.add_edge(row['sender'], row['receiver'], index=row.name)  

    try:
        loops = list(nx.simple_cycles(G))
        loop_nodes = set()
        for loop in loops:
            if len(loop) > 1:
                loop_nodes.update(loop)
        for i, row in df_tx.iterrows():
            if row['sender'] in loop_nodes and row['receiver'] in loop_nodes:
                labels[i] = 1
    except Exception as e:
        print("Cycle detection error:", e)

    df_tx['aml_label'] = labels
    return df_tx


def aml_predict():
    
    conn = psycopg2.connect(
        host="db",  
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        port=5432
    )
    
    wait_for_postgres()

    now = datetime.now(timezone.utc)
    four_hours_ago = now - timedelta(hours=4)

    query_tx = f"""
    SELECT * FROM ods.bitquery_records
    """
    df_tx = pd.read_sql_query(query_tx, conn)
    df_tx.rename(columns={"currency": "symbol"}, inplace=True)
    query_price = f"""
    SELECT 
        symbol, 
        AVG(current_price) AS price
    FROM ods.price_coingecko_quotes
    WHERE last_updated >= '{four_hours_ago.isoformat()}' AND last_updated <= '{now.isoformat()}'
    GROUP BY symbol
    """
    df_price = pd.read_sql_query(query_price, conn)
    df_result = predict(df_tx, df_price)

    df_output = df_result[['symbol', 'usdt_equivalent', 'aml_label']].copy()
    df_output.rename(columns={'usdt_equivalent': 'amount'}, inplace=True) 

    print(df_output.head())
    conn.close()

    return df_output
