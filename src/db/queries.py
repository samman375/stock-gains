###################################
# current_portfolio table queries #
###################################
def distinctTickersQuery():
    return """
        SELECT DISTINCT ticker, cost 
        FROM current_portfolio
        ORDER BY cost DESC;
    """

def currentPortfolioTickerQuery():
    return """
        SELECT 
            c.ticker, 
            c.cost, 
            c.volume, 
            c.total_brokerage, 
            COALESCE(SUM(d.distribution_value), 0)
        FROM current_portfolio c 
        LEFT JOIN dividends d ON c.ticker = d.ticker
        WHERE c.ticker = %s
        GROUP BY c.ticker, c.cost, c.volume, c.total_brokerage;
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


###################
# dividends table #
###################
def dividendsQuery():
    return """
        SELECT
            ticker,
            date,
            distribution_value
        FROM dividends
        ORDER BY date ASC;
    """

def dividendsInsert():
    return """
        INSERT INTO dividends (ticker, date, distribution_value)
        VALUES (%s, %s, %s);
    """


############################
# investment_history table #
############################
def investmentHistoryQuery():
    return """
        SELECT
            ticker,
            price,
            volume,
            brokerage,
            date,
            status
        FROM investment_history
        ORDER BY date ASC;
    """

def investmentHistoryInsert():
    return """
        INSERT INTO investment_history (ticker, price, volume, brokerage, date, status)
        VALUES (%s, %s, %s, %s, %s, %s);
    """
