import pandas as pd
from tabulate import tabulate
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

import utils.input_validation as v
from db.crud import getInvestmentHistory, getDividendHistory

TRADES_OUTPUT_COLUMNS = ['Date', 'Status', 'Ticker', 'Value ($)', 'Price ($)', 'Volume', 'Brokerage ($)']
DIVIDENDS_OUTPUT_COLUMNS = ['Date', 'Ticker', 'Distribution ($)']

def investmentHistory(conn, key_bindings):
    """
    Display investment history
    """
    completer = WordCompleter(['trades', 'dividends'], ignore_case=True)
    historyType = prompt("History type (trades/dividends): ", complete_while_typing=True, complete_in_thread=True, completer=completer, key_bindings=key_bindings)

    if historyType == "trades":
        trades = getInvestmentHistory(conn)
        tradesDfRows = []
        for trade in trades:
            date = trade[4]
            ticker = trade[0]
            status = trade[5]
            price = trade[1]
            volume = trade[2]
            value = price * volume
            brokerage = trade[3]
            
            tradesDfRows.append([date, status, ticker, value, price, volume, brokerage])

        df = pd.DataFrame(tradesDfRows, columns=TRADES_OUTPUT_COLUMNS)
        table = tabulate(df, headers='keys', tablefmt='rounded_grid', showindex=False)
        print(table)

    elif historyType == "dividends":
        dividends = getDividendHistory(conn)
        dividendsDfRows = []
        for dividend in dividends:
            date = dividend[1]
            ticker = dividend[0]
            distribution = dividend[2]

            dividendsDfRows.append([date, ticker, distribution])

        df = pd.DataFrame(dividendsDfRows, columns=DIVIDENDS_OUTPUT_COLUMNS)
        table = tabulate(df, headers='keys', tablefmt='rounded_grid', showindex=False)
        print(table)

    else:
        print("Invalid history type. Please try again.")
