from prompt_toolkit import prompt

import utils.input_validation as v
from db.crud import insertNewInvestmentHistory, reduceFromPortfolio

def sellInvestment(conn):
    """
    Add sale to database
    """
    ticker = prompt('Ticker: ', validator=v.TickerValidator(conn))
    price = float(prompt('Price: $', validator=v.NonNegativeFloatValidator()))
    volume = int(prompt('Volume: ', validator=v.NonNegativeIntValidator()))
    brokerage = float(prompt('Brokerage: $', validator=v.NonNegativeFloatValidator()))
    date = prompt('Date (YYYY-MM-DD): ', validator=v.DateValidator())
    profit = volume * price - brokerage

    try:
        with conn:
            insertNewInvestmentHistory(conn, ticker, price, volume, brokerage, date, 'SELL')
            reduceFromPortfolio(conn, ticker, price, volume, brokerage)
        
        print(f"Sold {volume} of {ticker} at ${price} per share on {date} with a ${brokerage} brokerage fee. Net trade value: ${profit}\n")
    
    except Exception as e:
        print(f"Failed to update database: {e}")
