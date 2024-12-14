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
