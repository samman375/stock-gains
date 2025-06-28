import pandas as pd
from tabulate import tabulate

from db.crud import getDistinctTickers
from fetchers.yfinance_fetcher import getYfinanceTickerData
from utils.data_processing import tickerValueExtractor

OUTPUT_COLUMNS = ['Ticker', 'Full Name', 'Price', 'Cost', 'Value', '%Gain', '%NetGain', 'Gain', 'Net Gain', 'Dividends']
MAX_COL_WIDTHS = [8, 23, 8, 9, 9, 7, 7, 9, 9, 9]

def portfolioValue(conn):
    """
    Print portfolio value table to command line sorted by cost

    Params:
    - conn: db connection
    """
    tickers = getDistinctTickers(conn)

    data = getYfinanceTickerData(conn, tickers)

    outputDfRows = []

    totalCost = 0
    totalValue = 0
    totalDividend = 0
    totalGain = 0
    totalNetGain = 0
    totalBrokerage = 0
    totalRealisedGains = 0

    soldPositionsTotalProfit = 0
    soldPositionDividends = 0
    soldPositionBrokerages = 0
    soldRealisedGains = 0

    for ticker in data.keys():
        tickerData = tickerValueExtractor(conn, data[ticker])
        tickerVolume = tickerData[3]

        if tickerVolume > 0:
            outputDfRows.append(convertDataRowToTableRow(tickerData[:-1]))

            totalCost += tickerData[4]
            totalValue += tickerData[5]
            totalDividend += tickerData[10]
            totalBrokerage += tickerData[11] + tickerData[12]
            totalRealisedGains += tickerData[13]
        else:
            # We want a row added for sold out positions to subtract from total cost
            soldRealisedGains += tickerData[13]
            soldPositionDividends += tickerData[10]
            soldPositionBrokerages += tickerData[11] + tickerData[12]
            soldPositionsTotalProfit += soldRealisedGains + soldPositionDividends - soldPositionBrokerages
    
    totalCost -= soldPositionsTotalProfit
    totalGain = totalValue - totalCost
    totalNetGain = (totalValue + totalDividend + totalRealisedGains) - (totalCost + totalBrokerage)

    if totalCost - soldPositionsTotalProfit <= 0:
        percGain = "N/A"
        netPercGain = "N/A"
    else:
        percGain = round((totalGain / totalCost) * 100, 2)
        netPercGain = round((totalNetGain / totalCost) * 100, 2)

    soldRow = [
        '',
        'Sold Out Positions',
        '',
        f'-{soldPositionsTotalProfit:.2f}',
        '',
        '',
        '',
        '',
        '',
        '',
    ]
    outputDfRows.append(soldRow)

    totalRow = [
        'Total', 
        '', 
        '', 
        f'{totalCost:.2f}', 
        f'{totalValue:.2f}', 
        f'{percGain:.2f}', 
        f'{netPercGain:.2f}', 
        f'{totalGain:.2f}', 
        f'{totalNetGain:.2f}', 
        f'{totalDividend:.2f}'
    ]
    outputDfRows.append(totalRow)

    df = pd.DataFrame(outputDfRows, columns=OUTPUT_COLUMNS)
    table = tabulate(df, headers='keys', tablefmt='rounded_grid', showindex=False, maxcolwidths=MAX_COL_WIDTHS)
    print(table)

def convertDataRowToTableRow(dataRow):
    return [
        dataRow[0],  # Ticker
        dataRow[1],  # Full Name
        f"{dataRow[2]:.2f}",  # Price
        f"{dataRow[4]:.2f}",  # Cost
        f"{dataRow[5]:.2f}",  # Value
        f"{dataRow[6]}",  # %Gain
        f"{dataRow[7]}",  # %NetGain
        f"{dataRow[8]:.2f}",  # Gain
        f"{dataRow[9]:.2f}",  # Net Gain
        f"{dataRow[10]:.2f}"  # Dividends
    ]