from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

import utils.input_validation as v
from db.crud import insertNewInvestmentHistory, getDistinctTickers

def buyInvestment(conn, key_bindings):
    """
    Add investment to database
    """
    try:
        # TODO: Fix validator + change to only validate at end
        availableTickers = getDistinctTickers(conn)
        tickerCompleter = WordCompleter(availableTickers, ignore_case=True) if availableTickers else None
        ticker = prompt('Ticker: ', completer=tickerCompleter, complete_while_typing=True, complete_in_thread=True, key_bindings=key_bindings).upper()
        price = float(prompt('Price: $', validator=v.NonNegativeFloatValidator(), key_bindings=key_bindings))
        volume = float(prompt('Volume: ', validator=v.NonNegativeFloatValidator(), key_bindings=key_bindings))
        brokerage = float(prompt('Brokerage: $', validator=v.NonNegativeFloatValidator(), key_bindings=key_bindings))
        date = prompt('Date (YYYY-MM-DD): ', validator=v.DateValidator(), key_bindings=key_bindings)
        
        cost = volume * price + brokerage

        try:
            with conn.cursor() as cur:
                insertNewInvestmentHistory(cur, ticker, price, volume, brokerage, date, 'BUY')
                conn.commit()
            print(f"Purchased {volume} of {ticker} at ${price} per share on {date} with a ${brokerage} brokerage fee. Net trade value: ${cost}\n")
        except Exception as e:
            conn.rollback()
            print(f"Failed to update database: {e}")
    except KeyboardInterrupt:
        print("Operation cancelled.")
