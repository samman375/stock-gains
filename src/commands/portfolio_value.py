import pandas as pd

from requests.yfinance_fetcher import getYfinanceTickerData
from utils.data_processing import tickerValueExtractor

def portfolioValue(conn):
    """
    Print portfolio value table to command line sorted by cost

    Params:
    - conn: db connection
    """

    data = getYfinanceTickerData()

    outputDfRows = []

    totalCost = 0
    totalValue = 0
    totalDividend = 0
    totalGain = 0
    totalNetGain = 0
    totalBrokerage = 0

    for ticker in data.keys():
        tickerData = tickerValueExtractor(conn, data[ticker])
        outputDfRows.append(tickerData[:-1])

        totalCost += tickerData[3]
        totalValue += tickerData[4]
        totalDividend += tickerData[9]
        totalGain += tickerData[7]
        totalNetGain += tickerData[8]
        totalBrokerage += tickerData[10]

    totalNetGain += totalDividend

    percGain = (totalValue / (totalCost - totalBrokerage) - 1) * 100
    netPercGain = (totalNetGain / totalCost) * 100

    totalRow = [
        '', 
        'Total', 
        '', 
        totalCost, 
        totalValue, 
        percGain, 
        netPercGain, 
        totalGain, 
        totalNetGain, 
        totalDividend
    ]
    outputDfRows.append(totalRow)

    outputColumns = ['Ticker', 'Full Name', 'Price', 'Cost', 'Value', '%Gain', '%NetGain', 'Gain', 'Net Gain', 'Dividends']
    df = pd.DataFrame(outputDfRows, columns=outputColumns)
    print(f'\n{df.to_string(index=False)}\n')
