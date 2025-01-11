from prompt_toolkit import prompt

import utils.input_validation as v
from db.crud import recordDividend

def dividend(conn):
    """
    Add dividend to database
    """
    ticker = prompt('Ticker: ', validator=v.ExistingTickerValidator(conn))
    value = prompt('Total Value: $', validator=v.NonNegativeFloatValidator())
    date = prompt('Date (YYYY-MM-DD): ', validator=v.DateValidator())

    try:
        with conn:
            recordDividend(conn, ticker, value, date)
            print(f"Recorded dividend received for {ticker} on {date} at value of ${value}\n")
    except Exception as e:
        print(f"Failed to update database: {e}")
