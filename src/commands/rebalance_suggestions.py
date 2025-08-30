import pandas as pd
from tabulate import tabulate
from prompt_toolkit import prompt

import utils.input_utils as i
import utils.input_validation as v
from db.crud import (
    getTargetBalance, 
    clearTargetBalance, 
    insertTargetBalance, 
    getCurrentPortfolioTickerData
)
from fetchers.yfinance_fetcher import getYfinanceTickerData
from utils.db_utils import postgresArrayToList
from utils.table_utils import formatPercentage, formatRatio, formatCurrency, formatTickerGroup

PORTFOLIO_BALANCE_OUTPUT_COLUMNS = ['Ticker Bucket', 'Target Percentage']
VALUATIONS_COLUMNS = ['Ticker', 'P/E Ratio', 'P/B Ratio', 'Beta', '52wk High Diff', '52wk Low Diff', '50-Day Avg Diff', '200-Day Avg Diff']
SUGGESTIONS_COLUMNS = ['Ticker Group', 'Current %', 'Target %', 'Value', 'Target Value', 'Suggestion']
COL_ALIGN_PORTFOLIO_BALANCE = ['left', 'right']
COL_ALIGN_VALUATIONS = ['left', 'right', 'right', 'right', 'right', 'right', 'right', 'right']
COL_ALIGN_SUGGESTIONS = ['left', 'right', 'right', 'right', 'right', 'right']

def updatePortfolioBalanceTargets(conn, key_bindings):
    """
    Update the target portfolio balance.
    """
    print('Provide ticker code and percentage.')
    print('To combine tickers separate using a `+`, such as: NDQ.AX+IVV.AX\n')

    try:
        balanceRows = {}
        percTotal = 0
        while percTotal < 100:
            ticker = prompt('Ticker(s): ', key_bindings=key_bindings)
            targetPerc = float(prompt(f'Current: {percTotal}%. Target percentage (%): ', validator=v.NonNegativeFloatValidator(), key_bindings=key_bindings))

            percTotal += targetPerc
            balanceRows[ticker] = targetPerc

        if percTotal > 100:
            print('Error: Total percentage cannot exceed 100%.')
            return False
    
    except KeyboardInterrupt:
        print("Operation cancelled. Proceeding with existing target balance.")
        return True

    clearTargetBalance(conn)
    with conn.cursor() as cur:
        for ticker, targetPerc in balanceRows.items():
            bucket = ticker.split('+')
            insertTargetBalance(cur, bucket, targetPerc)
        conn.commit()

    return True

def promptUpdatePortfolioBalanceTargets(conn, key_bindings):
    """
    Calls the function to update the portfolio balance targets until valid balance received.

    Returns:
    - targetBalance: The updated target balance.
    """
    balanceUpdated = False
    while not balanceUpdated:
        balanceUpdated = updatePortfolioBalanceTargets(conn, key_bindings)
    return getTargetBalance(conn)

def printPortfolioBalance(conn):
    """
    Print the current portfolio balance.
    """
    portfolioBalance = getTargetBalance(conn)
    if not portfolioBalance:
        print('No target portfolio balance set.')
        return

    portfolioBalanceDfRows = []
    for bucket, targetPerc in portfolioBalance:
        tickers = postgresArrayToList(bucket)
        portfolioBalanceDfRows.append([formatTickerGroup(tickers), formatPercentage(targetPerc)])

    df = pd.DataFrame(portfolioBalanceDfRows, columns=PORTFOLIO_BALANCE_OUTPUT_COLUMNS)
    table = tabulate(df, headers='keys', tablefmt='rounded_grid', showindex=False, colalign=COL_ALIGN_PORTFOLIO_BALANCE)
    print('\nCurrent Portfolio Balance Targets:')
    print(table)

def rebalanceSuggestions(conn, key_bindings):
    """
    Gives rebalance suggestions based on the current portfolio and target allocation.
    """
    targetBalance = getTargetBalance(conn)
    if not targetBalance:
        print('\nTarget portfolio balance input required.')
        targetBalance = promptUpdatePortfolioBalanceTargets(conn, key_bindings)

        if not targetBalance:
            print("No target balance set. Exiting.")
            return
    else:
        try:
            updateTargetBalance = i.getBoolInput('Update target balance? (Y/N): ', key_bindings=key_bindings)
        except KeyboardInterrupt:
            print("Operation cancelled. Proceeding with existing target balance.")
        
        if updateTargetBalance:
            targetBalance = promptUpdatePortfolioBalanceTargets(conn, key_bindings)

    printPortfolioBalance(conn)

    targetTotalValue = 0
    try:
        userHasTargetValue = i.getBoolInput('Do you have a total portfolio target in mind (Y/N)? ', key_bindings=key_bindings)
        if userHasTargetValue:
            targetTotalValue = float(prompt('Enter target value: $', validator=v.NonNegativeFloatValidator(), key_bindings=key_bindings))
    except KeyboardInterrupt:
        print("Operation cancelled. Proceeding with existing target balance.")

    # Create buckets dictionary with format:
    # {
    #     "NDQ.AX+IVV.AX":
    #         {
    #             "tickers": ["IVV.AX"+"NDQ.AX"],
    #             "value": 100000,
    #             "targetPerc": 25
    #         }
    # }

    totalValue = 0
    buckets = {}
    allTickers = []
    allLiveTickerData = {}

    # Get live data for all tickers in single yfinance call
    allTickers.extend([ticker for bucket in targetBalance for ticker in postgresArrayToList(bucket[0])])
    allLiveTickerData = getYfinanceTickerData(conn, allTickers)

    for bucket, perc in targetBalance:
        bucketInfo = {}
        bucketInfo['tickers'] = postgresArrayToList(bucket)
        bucketInfo['targetPerc'] = perc

        bucketValue = 0
        for ticker in bucketInfo['tickers']:
            volume = getCurrentPortfolioTickerData(conn, ticker)['volume']
            bucketValue += round(allLiveTickerData[ticker]['price'] * volume, 2)

        bucketInfo['value'] = bucketValue
        totalValue += bucketValue
        bucketName = '+'.join(bucketInfo['tickers'])
        buckets[bucketName] = bucketInfo

    highestPercDiff = 0
    highestBucket = ""
    for bucket in buckets:
        currentPerc = round((buckets[bucket]['value'] / totalValue) * 100, 2)
        buckets[bucket]['currentPerc'] = currentPerc
        targetPercDiff = (currentPerc - buckets[bucket]['targetPerc']) * (100 / buckets[bucket]['targetPerc'])
        if targetPercDiff >= highestPercDiff:
            highestPercDiff = targetPercDiff
            highestBucket = bucket
    
    if not targetTotalValue:
        targetTotalValue = buckets[highestBucket]['value'] * (100 / buckets[highestBucket]['targetPerc'])
    
    valuationsDfRows = []

    for ticker in allLiveTickerData:
        price = allLiveTickerData[ticker]['price']
        prcFromFiftyTwoWkHigh = round(((price - allLiveTickerData[ticker]['fiftyTwoWkHigh']) / allLiveTickerData[ticker]['fiftyTwoWkHigh']) * 100, 2)
        prcFromFiftyTwoWkLow = round(((price - allLiveTickerData[ticker]['fiftyTwoWkLow']) / allLiveTickerData[ticker]['fiftyTwoWkLow']) * 100, 2)
        prcFromFiftyDayAvg = round(((price - allLiveTickerData[ticker]['fiftyDayAvg']) / allLiveTickerData[ticker]['fiftyDayAvg']) * 100, 2)
        prcFromTwoHundredDayAvg = round(((price - allLiveTickerData[ticker]['twoHundredDayAvg']) / allLiveTickerData[ticker]['twoHundredDayAvg']) * 100, 2)

        valuationsDfRows.append([
            ticker,
            formatRatio(allLiveTickerData[ticker]['peRatio']),
            formatRatio(allLiveTickerData[ticker]['priceToBook']),
            formatRatio(allLiveTickerData[ticker]['beta']),
            formatPercentage(prcFromFiftyTwoWkHigh),
            formatPercentage(prcFromFiftyTwoWkLow),
            formatPercentage(prcFromFiftyDayAvg),
            formatPercentage(prcFromTwoHundredDayAvg)
        ])

    valuationsDf = pd.DataFrame(valuationsDfRows, columns=VALUATIONS_COLUMNS)
    table = tabulate(valuationsDf, headers='keys', tablefmt='rounded_grid', showindex=False, colalign=COL_ALIGN_VALUATIONS)
    print(table)

    suggestionsDfRows = []
    for bucket in buckets:
        targetValue = targetTotalValue * (buckets[bucket]['targetPerc'] / 100)
        targetDiff = targetValue - buckets[bucket]['value']

        suggestionsDfRows.append([
            formatTickerGroup(buckets[bucket]['tickers']),
            formatPercentage(round(buckets[bucket]['currentPerc'], 2)),
            formatPercentage(round(buckets[bucket]['targetPerc'], 2)),
            formatCurrency(round(buckets[bucket]['value'], 2)),
            formatCurrency(round(targetValue, 2)),
            formatCurrency(round(targetDiff, 2))
        ])

    suggestionsDf = pd.DataFrame(suggestionsDfRows, columns=SUGGESTIONS_COLUMNS)
    table = tabulate(suggestionsDf, headers='keys', tablefmt='rounded_grid', showindex=False, colalign=COL_ALIGN_SUGGESTIONS)
    print(table)
