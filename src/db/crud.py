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
        cur.execute(q.currentPortfolioTickerQuery(), (ticker,))
        return True if cur.fetchone() else False

    except psycopg2.Error as e:
        print(f"Database error: {e}")

def getCurrentPortfolioTickerData(conn, ticker):
    """
    Returns data from the current_portfolio table for a given ticker.
    Data currently returned: ticker, cost, volume, total_brokerage, dividends

    Params:
    - conn: db connection
    - ticker: ticker to lookup
    Returns:
    - tickerData: dictionary of data for the ticker
      eg. {'ticker': 'A200', 'cost': 500, ...}
    """
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(q.currentPortfolioTickerQuery(), (ticker,))
                result = cur.fetchone()
                tickerData = {
                    'ticker': result[0],
                    'cost': result[1],
                    'volume': result[2],
                    'total_brokerage': result[3],
                    'dividends': result[4]
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

def addToPortfolio(cur, ticker, price, volume, brokerage):
    """
    Updates the `current_portfolio` table with a new investment. 
    If the ticker already exists, it updates the values. 
    If the ticker does not exist, it inserts a new row.
    
    Note: Function does not contain a try/with block as it's meant to be use in an atomic function with a separate db call.

    Params:
    - conn: db connection
    - ticker (str): The ticker symbol.
    - price (float): The price of the investment.
    - volume (int): The volume of the investment.
    - brokerage (float): The brokerage fees.
    """
    isExistingTicker = checkIfTickerExists(cur, ticker)
    cost = price * volume + brokerage
    # cur = conn.cursor()
    if isExistingTicker:
        # Update existing record
        cur.execute(q.currentPortfolioBuyUpdate(), (cost, brokerage, volume, ticker,))
    else:
        # Insert new record
        cur.execute(q.currentPortfolioInsert(), (ticker, cost, brokerage, volume,))
    # cur.close()

def reduceFromPortfolio(cur, ticker, price, volume, brokerage):
    """
    Updates the `current_portfolio` table with a sale action. 
    If the ticker already exists, it updates the values.
    If the ticker value becomes non-positive, it deletes the row.
    
    Note: Function does not contain a try/with block as it's meant to be use in an atomic function with a separate db call.

    Params:
    - conn: db connection
    - ticker (str): The ticker symbol.
    - price (float): The price of the sale.
    - volume (int): The volume of the sale.
    - brokerage (float): The brokerage fees.
    """
    isExistingTicker = checkIfTickerExists(cur, ticker)
    profit = price * volume - brokerage
    if isExistingTicker:
        cur.execute(q.currentPortfolioSellUpdate(), (profit, brokerage, volume, ticker,))

        # Check if the volume is 0 or less and delete the row if true
        cur.execute(q.currentPortfolioDeleteIfZero(), (ticker,))
    else:
        raise Exception(f"Ticker {ticker} does not exist in portfolio. Nothing to sell")

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
