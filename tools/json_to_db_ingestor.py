"""
Helper script to data from old JSON files into PostgreSQL.
"""

import psycopg2
import json
from datetime import datetime

from db.db_handler import get_connection

def ingest_investment_history(data):
    """
    Ingests investment history JSON into PostgreSQL.
    
    :param data: Dictionary of investment records.
    :param db_params: Dictionary containing PostgreSQL connection details:
                      {'dbname': ..., 'user': ..., 'password': ..., 'host': ..., 'port': ...}
    """

    insert_query = """
    INSERT INTO investment_history (ticker, price, volume, brokerage, date, status)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT DO NOTHING;
    """

    try:
        conn = get_connection()
        cur = conn.cursor()
        
        for record in data.values():
            # Normalize the date from 'DD-MM-YYYY' to Python date object
            date_obj = datetime.strptime(record['date'], "%d-%m-%Y").date()
            values = (
                record['ticker'],
                float(record['price']),
                int(record['volume']),
                float(record['brokerage']),
                date_obj,
                record['status'].upper()
            )
            cur.execute(insert_query, values)

        conn.commit()
        cur.close()
        conn.close()
        print("Investment history successfully ingested.")

    except Exception as e:
        print("Error ingesting data:", e)

def ingest_dividends(data):
    """
    Ingests dividend data into the PostgreSQL 'dividends' table.

    :param data: Dictionary of dividend records.
    :param db_params: Dictionary with connection params:
                      {'dbname': ..., 'user': ..., 'password': ..., 'host': ..., 'port': ...}
    """

    insert_query = """
    INSERT INTO dividends (ticker, date, distribution_value)
    VALUES (%s, %s, %s)
    ON CONFLICT (ticker, date) DO NOTHING;
    """
    
    try:
        conn = get_connection()
        cur = conn.cursor()

        for record in data.values():
            date_obj = datetime.strptime(record['date'], "%d-%m-%Y").date()
            values = (
                record['ticker'],
                date_obj,
                float(record['value'])
            )
            cur.execute(insert_query, values)

        conn.commit()
        cur.close()
        conn.close()
        print("Dividends successfully ingested.")
    
    except Exception as e:
        print("Error ingesting dividends:", e)

def ingest_target_balance(data):
    """
    Ingests target balance data into the 'target_balance' table.

    :param data: Dictionary where each key is a ticker or '+'-joined tickers, and value is the target percentage.
    :param db_params: Dictionary with PostgreSQL connection params.
    """

    insert_query = """
    INSERT INTO target_balance (bucket_tickers, percentage)
    VALUES (%s, %s)
    ON CONFLICT (bucket_tickers) DO UPDATE 
        SET percentage = EXCLUDED.percentage;
    """

    try:
        conn = get_connection()
        cur = conn.cursor()

        for key, percentage in data.items():
            tickers = key.split('+')  # Split combined tickers into a list
            tickers_array = [ticker.strip() for ticker in tickers]
            cur.execute(insert_query, (tickers_array, float(percentage)))

        conn.commit()
        cur.close()
        conn.close()
        print("Target balance successfully ingested.")

    except Exception as e:
        print("Error ingesting target balance:", e)

if __name__ == "__main__":
    DIVIDEND_FILE = '../store/dividend_history.json'
    INVESTMENT_FILE = '../store/investment_history.json'
    TARGET_BALANCE_FILE = '../store/portfolio_balance.json'

    with open(INVESTMENT_FILE, 'r') as file:
        data = json.loads(file.read())
        ingest_investment_history(data)

    with open(DIVIDEND_FILE, 'r') as file:
        data = json.loads(file.read())
        ingest_dividends(data)

    with open(TARGET_BALANCE_FILE, 'r') as file:
        data = json.loads(file.read())
        ingest_target_balance(data)
