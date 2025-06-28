import psycopg2

import db.queries as q

def getDistinctTickers(conn):
    """
    Returns a list of all distinct tickers in current portfolio, ordered by cost
    """
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(q.distinctTickersQuery())
                result = cur.fetchall()

                tickers = [row[0] for row in result]

                return tickers

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []

def checkIfTickerExists(cur, ticker):
    """
    Checks if a ticker exists in the current_portfolio table.

    params:
    - conn: db connection cursor
    - ticker: ticker to check
    """
    try:
        cur.execute(q.tickerExistsQuery(), (ticker,))
        result = cur.fetchone()
        return result[0] if result is not None else False

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return False

def getCurrentPortfolioTickerData(conn, ticker):
    """
    Returns data from the current_portfolio table for a given ticker.
    Data currently returned: ticker, calculated_cost, total_volume, total_brokerage, total_dividends, realized_profit

    Params:
    - conn: db connection
    - ticker: ticker to lookup
    Returns:
    - tickerData: dictionary of data for the ticker
      eg. {'ticker': 'A200', 'calculated_cost': 500, ...}
    """
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(q.currentPortfolioTickerQuery(), (ticker,))
                result = cur.fetchone()
                if not result:
                    return {
                        'ticker': ticker,
                        'cost': 0.0,
                        'volume': 0,
                        'buy_brokerage': 0.0,
                        'sell_brokerage': 0.0,
                        'dividends': 0.0,
                        'realized_profit': 0.0
                    }
                else:
                    tickerData = {
                        'ticker': result[0],
                        'cost': float(result[1]) if result[1] is not None else None,
                        'volume': int(result[2]),
                        'buy_brokerage': float(result[3]),
                        'sell_brokerage': float(result[4]),
                        'dividends': float(result[5]),
                        'realized_profit': float(result[6])
                    }

                return tickerData

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []

def insertNewInvestmentHistory(cur, ticker, price, volume, brokerage, date, status):
    """
    Insert new investment history into investment_history table

    Note: Function does not contain a try/with block as it's meant to be use in an atomic function with a separate db call.

    Params:
    - cur: db connection cursor
    - ticker: ticker of the new investment
    - volume: volume of the new investment
    - price: price of the new investment
    - brokerage: brokerage of the new investment
    - date: date of the new investment
    - status: BUY or SELL status
    """
    cur.execute(q.investmentHistoryInsert(), (ticker, price, volume, brokerage, date, status,))
    cur.execute(q.refreshCurrentPortfolio())

def recordDividend(cur, ticker, value, date):
    """
    Records a dividend payment in the `dividends` table.

    Params:
    - conn: db connection
    - ticker (str): The ticker symbol.
    - value (float): The total value of the dividend.
    - date (str): The date of the dividend payment.
    """
    cur.execute(q.dividendsInsert(), (ticker, date, value,))
    cur.execute(q.refreshCurrentPortfolio())

def getInvestmentHistory(conn):
    """
    Returns all rows from the `investment_history` table.

    Params:
    - conn: db connection
    """
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(q.investmentHistoryQuery())
                return cur.fetchall()
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []

def getDividendHistory(conn):
    """
    Returns all rows from the `dividends` table.

    Params:
    - conn: db connection
    """
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(q.dividendsQuery())
                return cur.fetchall()
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []

def getTargetBalance(conn):
    """
    Returns the target balance for the portfolio from the `target_balance` table.

    Params:
    - conn: db connection
    """
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(q.targetBalanceQuery())
                return cur.fetchall()
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []

def clearTargetBalance(conn):
    """
    Clears the target balance for the portfolio from the `target_balance` table.

    Params:
    - conn: db connection
    """
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(q.truncateTargetBalance())
                conn.commit()
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []

def insertTargetBalance(cur, ticker, percentage):
    """
    Inserts a target balance into the `target_balance` table.

    Params:
    - conn: db connection
    - ticker (str): The ticker symbol.
    - percentage (float): The target percentage for the ticker.
    """
    cur.execute(q.insertTargetBalance(), (ticker, percentage,))
