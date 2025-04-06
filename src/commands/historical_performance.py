import pandas as pd
from tabulate import tabulate

from db.crud import getDistinctTickers
from fetchers.yfinance_fetcher import getYfinanceTickerData

OUTPUT_COLUMNS = ['Ticker', 'Name', 'YTD (%)', '3Y (%)', '5Y (%)', 'P/E Ratio']

def historicalPerformance(conn):
    """
    Given data from yfinance lookup, produces a dictionary of all required information for listing ticker performance.

    Params:
    - ticker: List of tickers to extract performance data for
    """
    tickers = getDistinctTickers(conn)
    if not tickers:
        print("No tickers found in current portfolio.")
        return

    data = getYfinanceTickerData(conn, tickers)

    outputDfRows = []

    for ticker in tickers:
        if ticker not in data:
            continue
        
        ytd = str("%.2f" % (data[ticker]['ytdReturn'] * 100)) if data[ticker]['ytdReturn'] else '- '
        threeYrReturn = str("%.2f" % (data[ticker]['threeYrReturn'] * 100)) if data[ticker]['threeYrReturn'] else '- '
        fiveYrReturn = str("%.2f" % (data[ticker]['fiveYrReturn'] * 100)) if data[ticker]['fiveYrReturn'] else '- '
        peRatio = str("%.2f" % data[ticker]['peRatio']) if data[ticker]['peRatio'] else '- '

        outputDfRows.append([
            ticker, 
            data[ticker]['fullName'],
            ytd,
            threeYrReturn,
            fiveYrReturn,
            peRatio
        ])

    df = pd.DataFrame(outputDfRows, columns=OUTPUT_COLUMNS)
    table = tabulate(df, headers='keys', tablefmt='rounded_grid', showindex=False)
    print(table)
