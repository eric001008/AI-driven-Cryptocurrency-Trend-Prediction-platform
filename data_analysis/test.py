import pandas as pd
import numpy as np
import random
import string
import networkx as nx
from datetime import datetime, timedelta


def random_address():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def generate_transaction_data(n=100):
    base_time = datetime.now()
    data = []

    A = "userA123"
    B = "userB456"
    C = "userC789"
    loop = [
        (A, B, 122),
        (B, C, 342),
        (C, A, 562),
    ]
    for i, (s, r, amt) in enumerate(loop):
        data.append({
            'date': (base_time + timedelta(seconds=i)).date(),
            'time': (base_time + timedelta(seconds=i)).time(),
            'sender': s,
            'receiver': r,
            'amount': amt,
            'symbol': 'ETH'
        })

    for i in range(n - len(loop)):
        sender = random_address()
        receiver = random_address()
        amount = round(random.uniform(0.001, 5), 8)
        currency = random.choice(['BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'XRP'])
        data.append({
            'date': (base_time + timedelta(seconds=i+3)).date(),
            'time': (base_time + timedelta(seconds=i+3)).time(),
            'sender': sender,
            'receiver': receiver,
            'amount': amount,
            'symbol': currency
        })

    return pd.DataFrame(data), [A, B, C]


def generate_price_data(symbols=50):
    symbol_list = random.sample([
        'BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE', 'DOT', 'MATIC',
        'TRX', 'AVAX', 'LTC', 'SHIB', 'WBTC', 'UNI', 'LINK', 'XLM', 'ATOM', 'ETC',
        'XMR', 'NEAR', 'FIL', 'EGLD', 'HBAR', 'APT', 'VET', 'ICP', 'KLAY', 'XTZ',
        'CRO', 'GRT', 'AAVE', 'MKR', 'ALGO', 'SAND', 'FTM', 'THETA', 'IMX', 'LDO',
        'AR', 'CHZ', 'ZIL', 'RUNE', 'DYDX', 'FLOW', 'BAT', 'ENS', 'CAKE', 'TWT'
    ], symbols)

    now = datetime.now()
    return pd.DataFrame([{
        'symbol': sym,
        'price': round(random.uniform(100, 60000), 2),
        'time': now
    } for sym in symbol_list])


from predict_aml import predict

df_tx, loop_addresses = generate_transaction_data()
df_price = generate_price_data()
df_result = predict(df_tx, df_price)

print("Starting AML detection test...")

# Check if constructed loop addresses were correctly flagged as suspicious
loop_set = set(loop_addresses)
suspicious_addrs = set(df_result[df_result['aml_label'] == 1]['sender']) | \
                   set(df_result[df_result['aml_label'] == 1]['receiver'])

missing = loop_set - suspicious_addrs
if missing:
    raise AssertionError(f"Loop addresses not properly flagged as suspicious. Missing: {missing}")
else:
    print(f"All loop addresses were correctly flagged as suspicious: {loop_set}")

# Check for false positives among random addresses
non_loop_df = df_result[~df_result['sender'].isin(loop_addresses) & ~df_result['receiver'].isin(loop_addresses)]
false_positives = non_loop_df[non_loop_df['aml_label'] == 1]

if not false_positives.empty:
    unique_fp = false_positives[['sender', 'receiver']].drop_duplicates()
    raise AssertionError(f"False positives detected among non-loop addresses:\n{unique_fp}")
else:
    print("No false positives: random addresses were not incorrectly flagged.")

print("AML detection test passed successfully.")

df_output = df_result[['symbol', 'usdt_equivalent', 'aml_label']].copy()
df_output.rename(columns={'usdt_equivalent': 'amount'}, inplace=True)  

print(df_output.head())
