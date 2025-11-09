import json
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

def getTickerPrice(tickerInfo):
    """
    Get price from ticker info dictionary

    Params:
    - tickerInfo: object with ticker information from yfinance
    """
    ask = tickerInfo.get('ask', None)
    previousClose = tickerInfo.get('previousClose', None)
    
    if ask is not None and ask > 0:
        return ask
    elif previousClose is not None and previousClose > 0:
        return previousClose
    else:
        return None
    
def getBeta(tickerInfo):
    """
    Get beta from ticker info dictionary

    Params:
    - tickerInfo: object with ticker information from yfinance
    """
    beta = tickerInfo.get('beta', None)
    beta3Yr = tickerInfo.get('beta3Year', None)

    if beta is not None:
        return beta
    elif beta3Yr is not None:
        return beta3Yr
    else:
        return None

def getYfinanceTickerData(conn, tickers, debug=False):
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
        if debug:
            print(json.dumps(tickerData.tickers[ticker].info, indent=2, sort_keys=True))

        data[ticker] = {
            'ticker': ticker,
            'price': getTickerPrice(tickerData.tickers[ticker].info),
            'fullName': tickerData.tickers[ticker].info.get('longName', None),
            'shortName': tickerData.tickers[ticker].info.get('shortName', None),
            'currency': tickerData.tickers[ticker].info.get('currency', None),
            'fullExchangeName': tickerData.tickers[ticker].info.get('fullExchangeName', None),
            'quoteType': tickerData.tickers[ticker].info.get('quoteType', None),
            'marketState': tickerData.tickers[ticker].info.get('marketState', None),
            'yield': tickerData.tickers[ticker].info.get('yield', 0),
            'quoteType': tickerData.tickers[ticker].info.get('quoteType', None),
            'peRatio': tickerData.tickers[ticker].info.get('trailingPE', None),
            'priceToBook': tickerData.tickers[ticker].info.get('priceToBook', None),
            'eps': tickerData.tickers[ticker].info.get('epsTrailingTwelveMonths', None),
            'volume': tickerData.tickers[ticker].info.get('volume', None),
            'beta': getBeta(tickerData.tickers[ticker].info),
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

def getYfinanceTickerHistory(conn, tickers, start_date):
    """
    Fetches historical daily price data for given tickers from start_date to today.
    
    Args:
        conn: Database connection
        tickers: List of ticker symbols
        start_date: Datetime object representing the earliest date to fetch
        
    Returns:
        Dictionary of dataframes containing daily price history for each ticker
    """
    tickers = makeTickerString(conn, tickers)
    historical_data = {}
    
    for ticker in tickers.split():
        try:
            yf_ticker = yf.Ticker(ticker)
            hist = yf_ticker.history(
                start=start_date,
                interval='1d',
                actions=True
            )
            if not hist.empty:
                historical_data[ticker] = hist
        except Exception as e:
            print(f"Error fetching historical data for {ticker}: {str(e)}")
            continue
            
    return historical_data
