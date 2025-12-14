DEFAULT_INDEX_TICKERS = [
    '^NDX',         # NASDAQ-100
    '^GSPC',        # S&P 500 Index
    '^AXJO',        # ASX 200
    '^N225',        # Nikkei 225
    '^HSI',         # Hang Seng Index
    '^FTSE',        # FTSE 100
    '^STOXX50E',    # EURO STOXX 50
    '^NSEI',        # Nifty 50
    'GC=F',         # Gold Futures
    'AUDUSD=X',     # AUD/USD Exchange Rate
    'BTC-USD',      # Bitcoin to USD
    '^VIX',         # CBOE Volatility Index
]

SUPPORTED_SETTINGS = {
    'debug_mode': {
        'type': 'boolean',
        'default': 'false',
        'description': 'Enable debug output in yfinance fetcher'
    },
    'indices_of_interest': {
        'type': 'json',
        'default': str(DEFAULT_INDEX_TICKERS),
        'description': 'List of indices to track in index performance'
    }
}

def getDefaultSetting(setting_name):
    """
    Get the default value for a setting.
    
    Params:
    - setting_name: name of the setting
    
    Returns:
    - default value if setting exists, None otherwise
    """
    if setting_name in SUPPORTED_SETTINGS:
        return SUPPORTED_SETTINGS[setting_name]['default']
    return None