from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

import utils.input_validation as v
from db.crud import insertNewInvestmentHistory, getDistinctTickersWithPositions

def sellInvestment(conn, key_bindings):
    """
    Add sale to database
    """
    try:
        availableTickers = getDistinctTickersWithPositions(conn)
        if not availableTickers:
            print("No tickers with active positions found in portfolio.")
            return
        tickerCompleter = WordCompleter(availableTickers, ignore_case=True)
        ticker = prompt('Ticker: ', completer=tickerCompleter, complete_while_typing=True, complete_in_thread=True, validator=v.ActivePositionTickerValidator(availableTickers), key_bindings=key_bindings).upper()
        price = float(prompt('Price: $', validator=v.NonNegativeFloatValidator(), key_bindings=key_bindings))
        volume = float(prompt('Volume: ', validator=v.NonNegativeFloatValidator(), key_bindings=key_bindings))
        brokerage = float(prompt('Brokerage: $', validator=v.NonNegativeFloatValidator(), key_bindings=key_bindings))
        date = prompt('Date (YYYY-MM-DD): ', validator=v.DateValidator(), key_bindings=key_bindings)
        profit = volume * price - brokerage

        try:
            with conn.cursor() as cur:
                insertNewInvestmentHistory(cur, ticker, price, volume, brokerage, date, 'SELL')
                conn.commit()

            print(f"Sold {volume} of {ticker} at ${price} per share on {date} with a ${brokerage} brokerage fee. Net trade value: ${profit}\n")

        except Exception as e:
            conn.rollback()
            print(f"Failed to update database: {e}")
    except KeyboardInterrupt:
        print("Operation cancelled.")
