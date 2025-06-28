##################################
# current_portfolio view queries #
##################################
def distinctTickersQuery():
    return """
        SELECT DISTINCT 
            ticker, 
            ROUND(total_volume * average_price, 2) AS calculated_cost
        FROM current_portfolio
        ORDER BY calculated_cost DESC;
    """

def tickerExistsQuery():
    return """
        SELECT EXISTS (
            SELECT 1 
            FROM current_portfolio 
            WHERE ticker = %s
        );
    """

def currentPortfolioTickerQuery():
    return """
        SELECT 
            c.ticker, 
            ROUND(c.total_volume * c.average_price, 2) AS calculated_cost, 
            c.total_volume, 
            c.buy_brokerage, 
            c.sell_brokerage,
            COALESCE(SUM(d.distribution_value), 0) AS total_dividends,
            c.realized_profit
        FROM current_portfolio c 
        LEFT JOIN dividends d ON c.ticker = d.ticker
        WHERE c.ticker = %s
        GROUP BY 
            c.ticker, 
            c.total_volume, 
            c.average_price, 
            c.buy_brokerage, 
            c.sell_brokerage,
            c.realized_profit;
    """

def refreshCurrentPortfolio():
    return """
        REFRESH MATERIALIZED VIEW current_portfolio;
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

########################
# target_balance table #
########################

def targetBalanceQuery():
    return """
        SELECT
            bucket_tickers,
            percentage
        FROM target_balance
        ORDER BY percentage DESC;
    """

def truncateTargetBalance():
    return """
        TRUNCATE target_balance;
    """

def insertTargetBalance():
    return """
        INSERT INTO target_balance (bucket_tickers, percentage)
        VALUES (%s, %s);
    """
