def distinctTickersQuery():
    return """
            SELECT DISTINCT ticker, cost 
            FROM current_portfolio
            ORDER BY cost DESC;
        """

def currentPortfolioTickerQuery():
    return """
        SELECT ticker, cost, volume, total_brokerage, dividends 
        FROM current_portfolio 
        WHERE ticker = %s;
    """

def investmentHistoryInsert():
    return """
        INSERT INTO investment_history (ticker, price, volume, brokerage, date, status)
        VALUES (%s, %s, %s, %s, %s, %s);
    """

def currentPortfolioBuyUpdate():
    return """
        UPDATE current_portfolio
        SET cost = cost + %s,
            total_brokerage = total_brokerage + %s,
            volume = volume + %s
        WHERE ticker = %s;
    """

def currentPortfolioSellUpdate():
    return """
        UPDATE current_portfolio
        SET cost = cost - %s,
            total_brokerage = total_brokerage + %s,
            volume = volume - %s
        WHERE ticker = %s;
    """

def currentPortfolioInsert():
    return """
        INSERT INTO current_portfolio (ticker, cost, total_brokerage, volume)
        VALUES (%s, %s, %s, %s);
    """

def currentPortfolioDeleteIfZero():
    return """
        DELETE FROM current_portfolio
        WHERE ticker = %s AND volume <= 0;
    """

def dividendsInsert():
    return """
        INSERT INTO dividends (ticker, date, distribution_value)
        VALUES (%s, %s, %s);
    """
