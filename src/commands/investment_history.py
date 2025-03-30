import pandas as pd
from tabulate import tabulate
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

import utils.input_validation as v
from db.crud import getInvestmentHistory

OUTPUT_COLUMNS = ['Date', 'Status', 'Ticker', 'Value ($)', 'Price ($)', 'Volume', 'Brokerage ($)']

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

        df = pd.DataFrame(tradesDfRows, columns=OUTPUT_COLUMNS)
        table = tabulate(df, headers='keys', tablefmt='rounded_grid', showindex=False)
        print(table)

    # elif history_type == "dividends":
    #     dividends = getInvestmentHistory(conn, 'DIVIDEND')
    #     print("Dividend history:")
    #     for dividend in dividends:
    #         print(dividend)
    else:
        print("Invalid history type. Please try again.")
