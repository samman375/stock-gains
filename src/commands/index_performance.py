import ast
import pandas as pd
from tabulate import tabulate

from db.crud import getSetting
from fetchers.yfinance_fetcher import getYfinanceTickerData
from utils.constants.defaults import DEFAULT_INDEX_TICKERS, getDefaultSetting
from utils.table_utils import formatPercentage, formatCurrency

OUTPUT_COLUMNS = ['Name', 'Exchange Name', 'Price', 'Currency', '52wk Diff', '52wk Low Diff', '52wk High Diff', '200-Day Avg Diff']
COL_ALIGN = ['left', 'left', 'right', 'left', 'right', 'right', 'right', 'right']
MAX_NAME_LENGTH = 25
MAX_COL_WIDTHS = [MAX_NAME_LENGTH, 11, 12, 8, 10, 10, 10, 10]
INDICES_SETTING_KEY = 'indices_of_interest'

def indexPerformance(conn):
    """
    Gets performance of key indices. Uses default indices if not set by settings.
    """
    default_indices = getDefaultSetting(INDICES_SETTING_KEY)
    indices_str = getSetting(conn, INDICES_SETTING_KEY, default_indices)
    try:
        indices = ast.literal_eval(indices_str)
    except (ValueError, SyntaxError):
        print("\nError parsing indices from settings. Using default indices.")
        indices = ast.literal_eval(default_indices)
    
    data = getYfinanceTickerData(conn, indices)    
    
    outputDfRows = []

    for index in indices:
        if index not in data:
            continue

        outputDfRows.append([
            getIndexDisplayName(data[index]),
            data[index]['fullExchangeName'] if data[index]['fullExchangeName'] else '-',
            formatCurrency(getIndexPrice(data[index]), includeDollarSign=False),
            data[index]['currency'],
            formatPercentage(data[index]['fiftyTwoWeekChangePercent']),
            formatPercentage(data[index]['fiftyTwoWeekLowChangePercent'] * 100),
            formatPercentage(data[index]['fiftyTwoWeekHighChangePercent'] * 100),
            formatPercentage(data[index]['twoHundredDayAverageChangePercent'] * 100)
        ])
    
    df = pd.DataFrame(outputDfRows, columns=OUTPUT_COLUMNS)
    table = tabulate(
        df, 
        headers='keys', 
        tablefmt='rounded_grid', 
        showindex=False, 
        colalign=COL_ALIGN,
        maxcolwidths=MAX_COL_WIDTHS
    )
    print(table)

def getIndexDisplayName(indexData):
    if indexData['fullName']:
        return indexData['fullName'][:MAX_NAME_LENGTH]
    elif indexData['shortName']:
        return indexData['shortName'][:MAX_NAME_LENGTH]
    else:
        return indexData['ticker'][:MAX_NAME_LENGTH]

def getIndexPrice(indexData):
    # print(indexData)
    return indexData['regularMarketPrice'] if indexData['regularMarketPrice'] is not None else indexData['regularMarketPreviousClose']