import pandas as pd
from tabulate import tabulate

from db.crud import getDistinctTickersWithPositions
from fetchers.yfinance_fetcher import getYfinanceTickerData
from utils.table_utils import formatPercentage, formatPeRatio

OUTPUT_COLUMNS = ['Ticker', 'Name', 'YTD', '3Y', '5Y', 'P/E Ratio']
COL_ALIGN = ['left', 'left', 'right', 'right', 'right', 'right']

def historicalPerformance(conn):
    """
    Given data from yfinance lookup, produces a dictionary of all required information for listing ticker performance.

    Params:
    - ticker: List of tickers to extract performance data for
    """
    tickers = getDistinctTickersWithPositions(conn)
    if not tickers:
        print("No tickers found in current portfolio.")
        return

    data = getYfinanceTickerData(conn, tickers)

    outputDfRows = []

    for ticker in tickers:
        if ticker not in data:
            continue
        
        ytd = formatPercentage(data[ticker]['ytdReturn'])
        threeYrReturn = formatPercentage(data[ticker]['threeYrReturn'] * 100 if data[ticker]['threeYrReturn'] is not None else None)
        fiveYrReturn = formatPercentage(data[ticker]['fiveYrReturn'] * 100 if data[ticker]['fiveYrReturn'] is not None else None)
        peRatio = formatPeRatio(data[ticker]['peRatio'])

        outputDfRows.append([
            ticker, 
            data[ticker]['fullName'],
            ytd,
            threeYrReturn,
            fiveYrReturn,
            peRatio
        ])

    df = pd.DataFrame(outputDfRows, columns=OUTPUT_COLUMNS)
    table = tabulate(df, headers='keys', tablefmt='rounded_grid', showindex=False, colalign=COL_ALIGN)
    print(table)
