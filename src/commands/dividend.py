from prompt_toolkit import prompt

import utils.input_validation as v
from db.crud import recordDividend

def dividend(conn, key_bindings):
    """
    Add dividend to database
    """
    try:
        ticker = prompt('Ticker: ', key_bindings=key_bindings)
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
