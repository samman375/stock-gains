from prompt_toolkit import prompt

import utils.input_validation as v
from db.crud import insertNewInvestmentHistory, addToPortfolio

def buyInvestment(conn):
    """
    Add investment to database
    """
    ticker = prompt('Ticker: ', validator=v.TickerValidator(conn))
    price = float(prompt('Price: $', validator=v.NonNegativeFloatValidator()))
    volume = int(prompt('Volume: ', validator=v.NonNegativeIntValidator()))
    brokerage = float(prompt('Brokerage: $', validator=v.NonNegativeFloatValidator()))
    date = prompt('Date (YYYY-MM-DD): ', validator=v.DateValidator())
    cost = volume * price + brokerage

    try:
        with conn:
            insertNewInvestmentHistory(conn, ticker, price, volume, brokerage, date, 'BUY')
            addToPortfolio(conn, ticker, price, volume, brokerage)
        print(f"Purchased {volume} of {ticker} at ${price} per share on {date} with a ${brokerage} brokerage fee. Net trade value: ${cost}\n")
    except Exception as e:
        print(f"Failed to update database: {e}")
