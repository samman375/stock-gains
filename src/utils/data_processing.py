from db.crud import getCurrentPortfolioTickerData

def tickerValueExtractor(conn, data:object):
    """
    Given data from yfinance lookup, produces a dictionary of all required information for listing ticker value.

    Params:
    - data: List for a single ticker from `getTickerData()`
        -> format: [ticker, fullName, price, cost, value, percGain, netPercGain, gain, netGain, dividend, totalBrokerage]
    """
    
    ticker = data['ticker']
    price = data['price']
    fullName = data['fullName']

    db_data = getCurrentPortfolioTickerData(conn, ticker)
    volume = db_data['volume']
    cost = db_data['cost']
    totalBrokerage = db_data['total_brokerage']
    dividend = db_data['dividends']

    value = price * volume
    percGain = round((value / (cost - totalBrokerage) - 1) * 100, 2)
    netPercGain = round(((value + dividend) / cost - 1) * 100, 2)
    gain = value - (cost - totalBrokerage)
    netGain = value + dividend - cost

    return [ticker, fullName, price, cost, value, percGain, netPercGain, gain, netGain, dividend, totalBrokerage]
