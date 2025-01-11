def distinctTickersQuery():
    return """
            SELECT DISTINCT ticker 
            FROM current_portfolio
            ORDER BY cost DESC;
        """

def currentPortfolioTickerQuery(ticker):
    return """
        SELECT ticker, cost, volume, total_brokerage, dividends 
        FROM current_portfolio 
        WHERE ticker = %s;
    """, (ticker)

def investmentHistoryInsert(ticker, price, volume, brokerage, date, status):
    return """
        INSERT INTO investment_history (ticker, price, volume, brokerage, date, status)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (ticker, price, volume, brokerage, date, status)

def currentPortfolioBuyUpdate(cost, brokerage, volume, ticker):
    return """
        UPDATE current_portfolio
        SET cost = cost + %s,
            total_brokerage = total_brokerage + %s,
            volume = volume + %s
        WHERE ticker = %s;
    """, (cost, brokerage, volume, ticker)

def currentPortfolioSellUpdate(profit, brokerage, volume, ticker):
    return """
        UPDATE current_portfolio
        SET cost = cost - %s,
            total_brokerage = total_brokerage + %s,
            volume = volume - %s
        WHERE ticker = %s;
    """, (profit, brokerage, volume, ticker)

def currentPortfolioInsert(ticker, cost, brokerage, volume):
    return """
        INSERT INTO current_portfolio (ticker, cost, total_brokerage, volume)
        VALUES (%s, %s, %s, %s);
    """, (ticker, cost, brokerage, volume)

def currentPortfolioDeleteIfZero(ticker):
    return """
        DELETE FROM current_portfolio
        WHERE ticker = %s AND volume <= 0;
    """, (ticker)

def dividendsInsert(ticker, date, value):
    return """
        INSERT INTO dividends (ticker, date, distribution_value)
        VALUES (%s, %s, %s);
    """, (ticker, date, value)
