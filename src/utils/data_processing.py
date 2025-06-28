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
    cost = db_data['cost'] if db_data['cost'] is not None else 0
    buyBrokerage = db_data['buy_brokerage']
    sellBrokerage = db_data['sell_brokerage']
    dividend = db_data['dividends']
    realizedProfit = db_data['realized_profit']

    if volume > 0:
        value = price * volume
        gain = value - cost
        netGain = (value + dividend + realizedProfit) - (cost + buyBrokerage + sellBrokerage)
        if cost != 0:
            percGain = round((gain / cost) * 100, 2)
            netPercGain = round((netGain / cost) * 100, 2)
        else:
            percGain = "N/A"
            netPercGain = "N/A"

        return [ticker, fullName, price, volume, cost, value, percGain, netPercGain, gain, netGain, dividend, buyBrokerage, sellBrokerage, realizedProfit]
    else:

        return [ticker, fullName, price, 0, 0, 0, 0, 0, 0, 0, dividend, buyBrokerage, sellBrokerage, realizedProfit]
