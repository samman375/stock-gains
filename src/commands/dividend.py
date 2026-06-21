from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

import utils.input_validation as v
from db.crud import recordDividend, getDistinctTickersWithPositions

def dividend(conn, key_bindings):
    """
    Add dividend to database
    """
    try:
        availableTickers = getDistinctTickersWithPositions(conn)
        if not availableTickers:
            print("No tickers with active positions found in portfolio.")
            return
        tickerCompleter = WordCompleter(availableTickers, ignore_case=True)
        ticker = prompt('Ticker: ', completer=tickerCompleter, complete_while_typing=True, complete_in_thread=True, validator=v.ActivePositionTickerValidator(availableTickers), key_bindings=key_bindings).upper()
        value = float(prompt('Total Value: $', validator=v.NonNegativeFloatValidator(), key_bindings=key_bindings))
        date = prompt('Date (YYYY-MM-DD): ', validator=v.DateValidator(), key_bindings=key_bindings)

        try:
            with conn.cursor() as cur:
                recordDividend(cur, ticker, value, date)
                print(f"Recorded dividend received for {ticker} on {date} at value of ${value}\n")
                conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Failed to update database: {e}")
    except KeyboardInterrupt:
        print("Operation cancelled.")
