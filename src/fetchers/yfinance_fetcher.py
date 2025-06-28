import yfinance as yf

from utils.yfinance_utils import makeTickerString

def isValidYfinanceTicker(ticker:str):
    """
    Check if ticker is valid in yfinance

    Params:
    - ticker: ticker to check
    """
    try:
        yf.Ticker(ticker)
        print("checking ticker: ", ticker)
        return True
    except:
        return False

def getYfinanceTickerData(conn, tickers):
    """
    Get data for tickers from Yahoo Finance API
    
    Params:
    - conn: connection to database
    - tickers: list of tickers

    Returns:
    - data: dictionary with ticker to information_dictionary key value mappings
    eg. {'IVV.AX': {'price': 100, 'volume': 10000, ...}, ...}
    """
    tickers = makeTickerString(conn, tickers)
    tickerData = yf.Tickers(tickers)
    data = {}
    for ticker in tickers.split():
        data[ticker] = {
            'ticker': ticker,
            'price': tickerData.tickers[ticker].info['ask'],
            'fullName': tickerData.tickers[ticker].info['longName'],
            'yield': tickerData.tickers[ticker].info.get('yield', 0),
            'quoteType': tickerData.tickers[ticker].info['quoteType'],
            'peRatio': tickerData.tickers[ticker].info.get('trailingPE', None),
            'volume': tickerData.tickers[ticker].info['volume'],
            'ytdReturn': tickerData.tickers[ticker].info.get('ytdReturn', None),
            'threeYrReturn': tickerData.tickers[ticker].info.get('threeYearAverageReturn', None),
            'fiveYrReturn': tickerData.tickers[ticker].info.get('fiveYearAverageReturn', None),
            'fiftyTwoWkLow': tickerData.tickers[ticker].info.get('fiftyTwoWeekLow', None),
            'fiftyTwoWkHigh': tickerData.tickers[ticker].info.get('fiftyTwoWeekHigh', None),
            'fiftyDayAvg': tickerData.tickers[ticker].info.get('fiftyDayAverage', None),
            'twoHundredDayAvg': tickerData.tickers[ticker].info.get('twoHundredDayAverage', None)
            # TODO: Add EPS, Beta, Market Cap
        }

    return data
