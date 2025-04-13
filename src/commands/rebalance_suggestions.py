import pandas as pd
from tabulate import tabulate
from prompt_toolkit import prompt

import utils.input_utils as i
import utils.input_validation as v
from db.crud import getTargetBalance, clearTargetBalance, insertTargetBalance

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
        print("Operation cancelled.")

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
        bucketString = ', '.join(bucket)
        portfolioBalanceDfRows.append([bucketString, targetPerc])

    df = pd.DataFrame(portfolioBalanceDfRows, columns=['Ticker Bucket', 'Target Percentage (%)'])
    table = tabulate(df, headers='keys', tablefmt='rounded_grid', showindex=False)
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
    else:
        updateTargetBalance = i.getBoolInput('Update target balance? (Y/N): ', key_bindings=key_bindings)
        if updateTargetBalance:
            targetBalance = promptUpdatePortfolioBalanceTargets(conn, key_bindings)

    printPortfolioBalance(conn)

    targetTotalValue = 0
    userHasTargetValue = i.getBoolInput('Do you have a total portfolio target in mind (Y/N)? ', key_bindings=key_bindings)
    if userHasTargetValue:
        targetTotalValue = float(prompt('Enter target value: $', validator=v.NonNegativeFloatValidator(), key_bindings=key_bindings))

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
    for bucket in targetBalance:
        buckets[bucket] = {} # TODO: Key can't be a list, recreate target_balance table
        allTickers.extend(bucket)
