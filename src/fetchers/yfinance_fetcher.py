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
            'price': tickerData.tickers[ticker].info.get('ask', None),
            'fullName': tickerData.tickers[ticker].info.get('longName', None),
            'shortName': tickerData.tickers[ticker].info.get('shortName', None),
            'currency': tickerData.tickers[ticker].info.get('currency', None),
            'fullExchangeName': tickerData.tickers[ticker].info.get('fullExchangeName', None),
            'quoteType': tickerData.tickers[ticker].info.get('quoteType', None),
            'marketState': tickerData.tickers[ticker].info.get('marketState', None),
            'yield': tickerData.tickers[ticker].info.get('yield', 0),
            'quoteType': tickerData.tickers[ticker].info.get('quoteType', None),
            'peRatio': tickerData.tickers[ticker].info.get('trailingPE', None),
            'volume': tickerData.tickers[ticker].info.get('volume', None),
            'ytdReturn': tickerData.tickers[ticker].info.get('ytdReturn', None),
            'threeYrReturn': tickerData.tickers[ticker].info.get('threeYearAverageReturn', None),
            'fiveYrReturn': tickerData.tickers[ticker].info.get('fiveYearAverageReturn', None),
            'fiftyTwoWkLow': tickerData.tickers[ticker].info.get('fiftyTwoWeekLow', None),
            'fiftyTwoWkHigh': tickerData.tickers[ticker].info.get('fiftyTwoWeekHigh', None),
            'fiftyDayAvg': tickerData.tickers[ticker].info.get('fiftyDayAverage', None),
            'regularMarketPrice': tickerData.tickers[ticker].info.get('regularMarketPrice', None),
            'regularMarketPreviousClose': tickerData.tickers[ticker].info.get('regularMarketPreviousClose', None),
            'twoHundredDayAvg': tickerData.tickers[ticker].info.get('twoHundredDayAverage', None),
            'fiftyTwoWeekChangePercent': tickerData.tickers[ticker].info.get('fiftyTwoWeekChangePercent', None),
            'fiftyTwoWeekLowChangePercent': tickerData.tickers[ticker].info.get('fiftyTwoWeekLowChangePercent', None),
            'fiftyTwoWeekHighChangePercent': tickerData.tickers[ticker].info.get('fiftyTwoWeekHighChangePercent', None),
            'twoHundredDayAverageChangePercent': tickerData.tickers[ticker].info.get('twoHundredDayAverageChangePercent', None)
        }

    return data
