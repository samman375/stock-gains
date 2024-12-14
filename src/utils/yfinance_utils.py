from db.crud import getDistinctTickers

def makeTickerString(conn, tickers=None):
    """
    Produces a string of space separated tickers for use in yfinance lookup.
    Fetches tickers from current portfolio if `None` provided to `tickers` parameter.

    Params:
    - conn: connection to database
    - tickers: list of tickers. Default: `None`
    """

    tickersStr = ""
    if not tickers:
        tickers = getDistinctTickers(conn)
    for ticker in tickers:
        tickersStr += f"{ticker} "
    return tickersStr.strip()
