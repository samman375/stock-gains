import psycopg2

def getDistinctTickers(conn):
    """
    Returns a list of all distinct tickers in current portfolio, ordered by cost
    """
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT DISTINCT ticker 
                    FROM current_portfolio
                    ORDER BY cost DESC;
                """)
                result = cur.fetchall()

                tickers = [row[0] for row in result]

                return tickers

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []

def checkIfTickerExists(conn, ticker):
    """
    Checks if a ticker exists in the current_portfolio table.

    params:
    - conn: db connection
    - ticker: ticker to check
    """
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM current_portfolio WHERE ticker = %s;", (ticker,))
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
                cur.execute("""
                    SELECT ticker, cost, volume, total_brokerage, dividends
                    FROM current_portfolio
                    WHERE ticker = %s;
                """, (ticker,))
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

def insertNewInvestmentHistory(conn, ticker, price, volume, brokerage, date, status):
    """
    Insert new investment history into investment_history table

    Note: Function does not contain a try/with block as it's meant to be use in an atomic function with a separate db call.

    Params:
    - conn: db connection
    - ticker: ticker of the new investment
    - volume: volume of the new investment
    - price: price of the new investment
    - brokerage: brokerage of the new investment
    - date: date of the new investment
    - status: BUY or SELL status
    """
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO investment_history (ticker, price, volume, brokerage, date, status)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (ticker, price, volume, brokerage, date, status))
    cur.close()

def addToPortfolio(conn, ticker, price, volume, brokerage):
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
    isExistingTicker = checkIfTickerExists(conn, ticker)
    cost = price * volume + brokerage
    cur = conn.cursor()
    if isExistingTicker:
        # Update existing record
        cur.execute("""
            UPDATE current_portfolio
            SET cost = cost + %s,
                total_brokerage = total_brokerage + %s,
                volume = volume + %s
            WHERE ticker = %s;
        """, (cost, brokerage, volume, ticker))
    else:
        # Insert new record
        cur.execute("""
            INSERT INTO current_portfolio (ticker, cost, total_brokerage, volume)
            VALUES (%s, %s, %s, %s);
        """, (ticker, cost, brokerage, volume))
    cur.close()

def reduceFromPortfolio(conn, ticker, price, volume, brokerage):
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
    isExistingTicker = checkIfTickerExists(conn, ticker)
    profit = price * volume - brokerage
    cur = conn.cursor()
    if isExistingTicker:
        cur.execute("""
            UPDATE current_portfolio
            SET cost = cost - %s,
                total_brokerage = total_brokerage + %s,
                volume = volume - %s
            WHERE ticker = %s;
        """, (profit, brokerage, volume, ticker))

        # Check if the volume is 0 or less and delete the row if true
        cur.execute("""
            DELETE FROM current_portfolio
            WHERE ticker = %s AND volume <= 0;
        """, (ticker))
    else:
        raise Exception(f"Ticker {ticker} does not exist in portfolio. Nothing to sell")
    cur.close()

def recordDividend(conn, ticker, value, date):
    """
    Records a dividend payment in the `dividends` table.

    Params:
    - conn: db connection
    - ticker (str): The ticker symbol.
    - value (float): The total value of the dividend.
    - date (str): The date of the dividend payment.
    """
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO dividends (ticker, date, distribution_value)
                    VALUES (%s, %s, %s, %s);
                """, (ticker, date, value))
    except psycopg2.Error as e:
        print(f"Database error: {e}")
