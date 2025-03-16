from prompt_toolkit import prompt

import utils.input_validation as v
from db.crud import insertNewInvestmentHistory, addToPortfolio

def buyInvestment(conn, key_bindings):
    """
    Add investment to database
    """
    try:
        # TODO: Fix validator + change to only validate at end
        ticker = prompt('Ticker: ', key_bindings=key_bindings)
        price = float(prompt('Price: $', validator=v.NonNegativeFloatValidator(), key_bindings=key_bindings))
        volume = int(prompt('Volume: ', validator=v.NonNegativeIntValidator(), key_bindings=key_bindings))
        brokerage = float(prompt('Brokerage: $', validator=v.NonNegativeFloatValidator(), key_bindings=key_bindings))
        date = prompt('Date (YYYY-MM-DD): ', validator=v.DateValidator(), key_bindings=key_bindings)
        cost = volume * price + brokerage

        try:
            with conn.cursor() as cur:
                insertNewInvestmentHistory(conn, ticker, price, volume, brokerage, date, 'BUY')
                addToPortfolio(conn, ticker, price, volume, brokerage)
                conn.commit()
            print(f"Purchased {volume} of {ticker} at ${price} per share on {date} with a ${brokerage} brokerage fee. Net trade value: ${cost}\n")
        except Exception as e:
            conn.rollback()
            print(f"Failed to update database: {e}")
    except KeyboardInterrupt:
        print("Operation cancelled.")
