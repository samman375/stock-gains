import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from tabulate import tabulate

from db.crud import getDistinctTickers
from fetchers.yfinance_fetcher import getYfinanceTickerData, getYfinanceTickerHistory
from utils.table_utils import formatPercentage, formatCurrency

OVERALL_COLUMNS = ['Period', 'Total Return', 'Pure Return']
TICKER_COLUMNS = ['Ticker', 'YTD', '1Y', '2Y p.a.', '3Y p.a.', '5Y p.a.']
COL_ALIGN_OVERALL = ['left', 'right', 'right']
COL_ALIGN_TICKER = ['left'] + ['right'] * (len(TICKER_COLUMNS) - 1)

def calculate_period_return(ticker_data, transactions, dividends, start_date, end_date):
    """
    Calculate returns for a specific period, including dividends.
    Returns both total return and pure (time-weighted) return.
    """
    if ticker_data.empty:
        return None, None
        
    # Get prices at start and end
    start_price = ticker_data.loc[start_date:start_date]['Close'].iloc[0] if start_date in ticker_data.index else None
    end_price = ticker_data.loc[end_date:end_date]['Close'].iloc[-1] if end_date in ticker_data.index else None
    
    if start_price is None or end_price is None:
        return None, None
        
    # Get transactions in period
    period_transactions = transactions[(transactions['date'] >= start_date) & 
                                    (transactions['date'] <= end_date)]
    
    # Get dividends in period
    period_dividends = dividends[(dividends['date'] >= start_date) & 
                               (dividends['date'] <= end_date)]
    
    # Calculate total return including cash flows
    total_invested = period_transactions[period_transactions['status'] == 'BUY']['price'].sum()
    total_withdrawn = period_transactions[period_transactions['status'] == 'SELL']['price'].sum()
    total_dividends = period_dividends['distribution_value'].sum()
    
    if total_invested == 0:
        return None, None
        
    total_return = ((end_price - start_price) / start_price) + (total_dividends / total_invested)
    
    # Calculate pure return (time-weighted)
    daily_returns = ticker_data['Close'].pct_change()
    pure_return = (1 + daily_returns).prod() - 1
    
    return total_return, pure_return

def annualize_return(total_return, years):
    """Convert total return to annualized return"""
    if total_return is None or total_return <= -1:
        return None
    return (1 + total_return) ** (1/years) - 1

def portfolioGrowth(conn):
    """
    Calculates and displays portfolio growth over different time periods:
    - YTD
    - 1 Year
    - 2 Year (p.a.)
    - 3 Year (p.a.)
    - 5 Year (p.a.)
    
    Shows both total return (including contributions) and pure return (time-weighted)
    """
    tickers = getDistinctTickers(conn)
    if not tickers:
        print("No tickers found in portfolio.")
        return

    # Get current data and historical prices
    current_data = getYfinanceTickerData(conn, tickers)
    
    # Calculate dates for different periods
    today = datetime.now()
    ytd_start = datetime(today.year, 1, 1)
    one_year_ago = today - timedelta(days=365)
    two_years_ago = today - timedelta(days=730)
    three_years_ago = today - timedelta(days=1095)
    five_years_ago = today - timedelta(days=1825)
    
    dates_needed = [ytd_start, one_year_ago, two_years_ago, three_years_ago, five_years_ago]
    historical_data = getYfinanceTickerHistory(conn, tickers, min(dates_needed))
    
    # Get transaction and dividend data from database
    with conn.cursor() as cur:
        # Get all transactions
        cur.execute("""
            SELECT ticker, date, status, price * volume as amount, brokerage 
            FROM investment_history 
            ORDER BY date
        """)
        transactions = pd.DataFrame(cur.fetchall(), 
                                  columns=['ticker', 'date', 'status', 'amount', 'brokerage'])
        
        # Get all dividends
        cur.execute("SELECT ticker, date, distribution_value FROM dividends ORDER BY date")
        dividends = pd.DataFrame(cur.fetchall(), 
                               columns=['ticker', 'date', 'distribution_value'])
    
    # Calculate returns for each ticker
    ticker_returns = []
    for ticker in tickers:
        if ticker not in historical_data:
            continue
            
        ticker_hist = historical_data[ticker]
        ticker_trans = transactions[transactions['ticker'] == ticker]
        ticker_divs = dividends[dividends['ticker'] == ticker]
        
        ytd_return = calculate_period_return(ticker_hist, ticker_trans, ticker_divs, 
                                           ytd_start, today)[0]
        one_yr_return = calculate_period_return(ticker_hist, ticker_trans, ticker_divs, 
                                              one_year_ago, today)[0]
        two_yr_return = annualize_return(calculate_period_return(ticker_hist, ticker_trans, 
                                                               ticker_divs, two_years_ago, today)[0], 2)
        three_yr_return = annualize_return(calculate_period_return(ticker_hist, ticker_trans, 
                                                                 ticker_divs, three_years_ago, today)[0], 3)
        five_yr_return = annualize_return(calculate_period_return(ticker_hist, ticker_trans, 
                                                                ticker_divs, five_years_ago, today)[0], 5)
        
        ticker_returns.append([
            ticker,
            formatPercentage(ytd_return * 100 if ytd_return else None),
            formatPercentage(one_yr_return * 100 if one_yr_return else None),
            formatPercentage(two_yr_return * 100 if two_yr_return else None),
            formatPercentage(three_yr_return * 100 if three_yr_return else None),
            formatPercentage(five_yr_return * 100 if five_yr_return else None)
        ])
    
    # Calculate overall portfolio returns
    portfolio_returns = []
    for period_start, period_name, years in [
        (ytd_start, 'YTD', None),
        (one_year_ago, '1 Year', 1),
        (two_years_ago, '2 Year (p.a.)', 2),
        (three_years_ago, '3 Year (p.a.)', 3),
        (five_years_ago, '5 Year (p.a.)', 5)
    ]:
        total_return, pure_return = 0, 0
        valid_returns = 0
        
        for ticker in tickers:
            if ticker not in historical_data:
                continue
                
            returns = calculate_period_return(
                historical_data[ticker],
                transactions[transactions['ticker'] == ticker],
                dividends[dividends['ticker'] == ticker],
                period_start,
                today
            )
            
            if returns[0] is not None:
                if years:  # Annualize if needed
                    total_return += annualize_return(returns[0], years) or 0
                    pure_return += annualize_return(returns[1], years) or 0
                else:
                    total_return += returns[0]
                    pure_return += returns[1]
                valid_returns += 1
        
        if valid_returns > 0:
            total_return /= valid_returns
            pure_return /= valid_returns
        
        portfolio_returns.append([
            period_name,
            formatPercentage(total_return * 100),
            formatPercentage(pure_return * 100)
        ])
    
    # Display results
    print("\nPortfolio Growth Summary:")
    overall_df = pd.DataFrame(portfolio_returns, columns=OVERALL_COLUMNS)
    overall_table = tabulate(overall_df, headers='keys', tablefmt='rounded_grid', 
                           showindex=False, colalign=COL_ALIGN_OVERALL)
    print(overall_table)
    
    print("\nTicker-Level Performance:")
    ticker_df = pd.DataFrame(ticker_returns, columns=TICKER_COLUMNS)
    ticker_table = tabulate(ticker_df, headers='keys', tablefmt='rounded_grid', 
                          showindex=False, colalign=COL_ALIGN_TICKER)
    print(ticker_table)
    
    print("\nNote:")
    print("- Total Return includes the impact of capital contributions and withdrawals")
    print("- Pure Return shows investment performance independent of cash flows")
    print("- Returns are calculated including dividends")
    print("- p.a. indicates annualized returns for multi-year periods")