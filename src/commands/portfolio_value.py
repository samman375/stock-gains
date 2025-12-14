import pandas as pd
from tabulate import tabulate

from db.crud import getDistinctTickers
from fetchers.yfinance_fetcher import getYfinanceTickerData
from utils.data_processing import tickerValueExtractor
from utils.table_utils import formatCurrency, formatPercentage

OUTPUT_COLUMNS_FULL = ['Ticker', 'Full Name', 'Price', 'Vol', 'Cost', 'Value', 'Dividends', 'Gain', 'Net Gain', '% Gain', '% NetGain']
OUTPUT_COLUMNS_MIN = ['Ticker', 'Cost', 'Value', 'Dividends', 'Gain', 'Net Gain', '% Gain', '% NetGain']
MAX_COL_WIDTHS_FULL = [8, 30, 8, 6, 11, 11, 10, 10, 10, 7, 7]
MAX_COL_WIDTHS_MIN = [8, 11, 11, 10, 10, 10, 7, 7]
COL_ALIGN_FULL = ['left', 'left'] + ['right'] * (len(OUTPUT_COLUMNS_FULL) - 2)
COL_ALIGN_MIN = ['left'] + ['right'] * (len(OUTPUT_COLUMNS_MIN) - 1)

# Indices of columns to keep for minimal output
MINIMAL_INDICES = [0, 4, 5, 6, 7, 8, 9, 10]

def portfolioValue(conn, fullOutput=False):
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
            row = convertDataRowToTableRow(tickerData[:-1])
            if not fullOutput:
                row = [row[i] for i in MINIMAL_INDICES]
            outputDfRows.append(row)

            totalCost += tickerData[4]
            totalValue += tickerData[5]
            totalDividend += tickerData[10]
            totalBrokerage += tickerData[11] + tickerData[12]
            totalRealisedGains += tickerData[13]
        else:
            currentTickerRealisedGains = tickerData[13]
            currentTickerDividends = tickerData[10]
            currentTickerBrokerage = tickerData[11] + tickerData[12]

            soldRealisedGains += currentTickerRealisedGains
            soldPositionDividends += currentTickerDividends
            soldPositionBrokerages += currentTickerBrokerage

            tickerProfit = currentTickerRealisedGains + currentTickerDividends - currentTickerBrokerage
            soldPositionsTotalProfit += tickerProfit

            if debug:
                print(f"\nFor ticker {ticker}:")
                print(f"  Realised Gains: {formatCurrency(currentTickerRealisedGains)}")
                print(f"  Dividends: {formatCurrency(currentTickerDividends)}")
                print(f"  Total Brokerage: {formatCurrency(currentTickerBrokerage)}")
                print(f"  Ticker Profit: {formatCurrency(tickerProfit)}")
                print(f"Running total of Sold Positions Profit: {formatCurrency(soldPositionsTotalProfit)}")

    totalCost -= soldPositionsTotalProfit
    totalGain = totalValue - totalCost
    totalNetGain = (totalValue + totalDividend + totalRealisedGains) - (totalCost + totalBrokerage)

    if totalCost <= 0:
        percGain = "N/A"
        netPercGain = "N/A"
    else:
        percGain = round((totalGain / totalCost) * 100, 2)
        netPercGain = round((totalNetGain / totalCost) * 100, 2)

    soldRow = [
        '*',
        'Sold Out Positions',
        '-',
        '-',
        formatCurrency(soldPositionsTotalProfit * -1),
        '-',
        '-',
        '-',
        '-',
        '-',
        '-',
    ]
    if not fullOutput:
        soldRow = [soldRow[i] for i in MINIMAL_INDICES]
    outputDfRows.append(soldRow)

    totalRow = [
        'Total', 
        '', 
        '', 
        '',
        formatCurrency(totalCost), 
        formatCurrency(totalValue), 
        formatCurrency(totalDividend),
        formatCurrency(totalGain), 
        formatCurrency(totalNetGain), 
        formatPercentage(percGain), 
        formatPercentage(netPercGain)
    ]
    if not fullOutput:
        totalRow = [totalRow[i] for i in MINIMAL_INDICES]
    outputDfRows.append(totalRow)

    if fullOutput:
        df = pd.DataFrame(outputDfRows, columns=OUTPUT_COLUMNS_FULL)
        table = tabulate(
            df, 
            headers='keys', 
            tablefmt='rounded_grid', 
            showindex=False, 
            maxcolwidths=MAX_COL_WIDTHS_FULL,
            colalign=COL_ALIGN_FULL
        )
    else:
        df = pd.DataFrame(outputDfRows, columns=OUTPUT_COLUMNS_MIN)
        table = tabulate(
            df, 
            headers='keys', 
            tablefmt='rounded_grid', 
            showindex=False, 
            maxcolwidths=MAX_COL_WIDTHS_MIN,
            colalign=COL_ALIGN_MIN
        )
    print(table)

def convertDataRowToTableRow(dataRow):
    return [
        dataRow[0],                     # Ticker
        dataRow[1],                     # Full Name
        formatCurrency(dataRow[2]),     # Price
        dataRow[3],                     # Volume
        formatCurrency(dataRow[4]),     # Cost
        formatCurrency(dataRow[5]),     # Value
        formatCurrency(dataRow[10]),    # Dividends
        formatCurrency(dataRow[8]),     # Gain
        formatCurrency(dataRow[9]),     # Net Gain
        formatPercentage(dataRow[6]),   # %Gain
        formatPercentage(dataRow[7])    # %NetGain
    ]
