import pandas as pd
from tabulate import tabulate
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from db.crud import getInvestmentHistory, getDividendHistory, getInvestmentHistoryByTicker, getDividendHistoryByTicker, getDistinctTickers
from utils.table_utils import formatCurrency

TRADES_OUTPUT_COLUMNS = ['Date', 'Status', 'Ticker', 'Volume', 'Price ($)', 'Value ($)', 'Brokerage ($)']
DIVIDENDS_OUTPUT_COLUMNS = ['Date', 'Ticker', 'Distribution ($)']
COL_ALIGN_TRADES = ['left', 'left', 'left'] + ['right'] * (len(TRADES_OUTPUT_COLUMNS) - 3)
COL_ALIGN_DIVIDENDS = ['left', 'left', 'right']

def investmentHistory(conn, key_bindings, ticker=None):
    """
    Display investment history, optionally filtered by ticker
    
    Params:
    - conn: database connection
    - key_bindings: key bindings for prompt
    - ticker: optional ticker to filter by (if not provided, user will be prompted)
    """
    try:
        completer = WordCompleter(['trades', 'dividends'], ignore_case=True)
        historyType = prompt("History type (trades/dividends): ", complete_while_typing=True, complete_in_thread=True, completer=completer, key_bindings=key_bindings)

        # If ticker not provided as argument, ask if user wants to filter by ticker
        if ticker is None:
            filterCompleter = WordCompleter(['yes', 'no'], ignore_case=True)
            filterByTicker = prompt("Filter by ticker? (yes/no): ", complete_while_typing=True, complete_in_thread=True, completer=filterCompleter, key_bindings=key_bindings).lower()
            
            if filterByTicker == "yes":
                availableTickers = getDistinctTickers(conn)
                if not availableTickers:
                    print("No tickers found in portfolio.")
                    return
                
                print(f"Available tickers: {', '.join(availableTickers)}")
                tickerCompleter = WordCompleter(availableTickers, ignore_case=True)
                ticker = prompt("Select ticker: ", complete_while_typing=True, complete_in_thread=True, completer=tickerCompleter, key_bindings=key_bindings).upper()
                
                if ticker not in availableTickers:
                    print(f"Invalid ticker: {ticker}")
                    return
        else:
            # Validate the provided ticker
            availableTickers = getDistinctTickers(conn)
            if ticker not in availableTickers:
                print(f"Invalid ticker: {ticker}. Available tickers: {', '.join(availableTickers)}")
                return

        if historyType == "trades":
            if ticker:
                trades = getInvestmentHistoryByTicker(conn, ticker)
            else:
                trades = getInvestmentHistory(conn)
            
            tradesDfRows = []
            for trade in trades:
                date = trade[4]
                ticker_data = trade[0]
                status = trade[5]
                price = trade[1]
                volume = trade[2]
                value = price * volume
                brokerage = trade[3]
                
                tradesDfRows.append([
                    date, 
                    status, 
                    ticker_data, 
                    volume, 
                    formatCurrency(price), 
                    formatCurrency(value), 
                    formatCurrency(brokerage)
                ])

            df = pd.DataFrame(tradesDfRows, columns=TRADES_OUTPUT_COLUMNS)
            table = tabulate(df, headers='keys', tablefmt='rounded_grid', showindex=False, colalign=COL_ALIGN_TRADES)
            print(table)

        elif historyType == "dividends":
            if ticker:
                dividends = getDividendHistoryByTicker(conn, ticker)
            else:
                dividends = getDividendHistory(conn)
            
            dividendsDfRows = []
            for dividend in dividends:
                date = dividend[1]
                ticker_data = dividend[0]
                distribution = dividend[2]

                dividendsDfRows.append([date, ticker_data, formatCurrency(distribution)])

            df = pd.DataFrame(dividendsDfRows, columns=DIVIDENDS_OUTPUT_COLUMNS)
            table = tabulate(df, headers='keys', tablefmt='rounded_grid', showindex=False, colalign=COL_ALIGN_DIVIDENDS)
            print(table)

        else:
            print("Invalid history type. Please try again.")

    except KeyboardInterrupt:
        print("Operation cancelled.")
