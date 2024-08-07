from investments import Investments


inv = Investments()

print("stock-gains: Command-line stock valuation tool\n")
print("Enter 'help' for list of commands.")

while True:
    command = input('Command: ').lower().strip()
    if command == 'help' or command == 'h':
        help = """
        'b' or 'buy' :          Add new investment purchase
        's' or 'sell':          Add new sale purchase
        'v' or 'value':         Get total portfolio value
        't' or 'ticker-value':  Get value of specific owned ticker
        'tp' pr 'ticker-perf':  Get performance for a particular ticker
        'hs' or 'history':      Investment history
        'd' or 'dividend':      Add received dividend
        'e' or 'estimate':      Get dividend estimate for next 12 months
        'p' or 'performance':   Get historical stock performance
        'ipc' or 'inv-perc':    Get portfolio percentage share for each investment
        'mpc' or 'mkt-perc':    Get portfolio percentage share for each market
        'r' or 'rebalance':     Get suggestions on where to invest to rebalance portfolio
        'h' or 'help':          Help
        'q' or 'quit':          Quit
        """
        print(help)

    elif command == 'buy' or command == 'b':
        ticker = input('Ticker: ').strip()
        price = float(input('Price: $').strip())
        volume = int(input('Volume: ').strip())
        brokerage = float(input('Brokerage: $').strip())
        date = input('Date (DD-MM-YYYY): ').strip()
        inv.buyInvestment(ticker, price, volume, brokerage, date)

    elif command == 'sell' or command == 's':
        ticker = input('Ticker: ').strip()
        price = float(input('Price: $').strip())
        volume = int(input('Volume: ').strip())
        brokerage = float(input('Brokerage: $').strip())
        date = input('Date (DD-MM-YYYY): ').strip()
        inv.sellInvestment(ticker, price, volume, brokerage, date)

    elif command == 'ticker-value' or command == 't':
        ticker = input("Ticker Code: ").strip()
        inv.investmentValue(ticker)
    
    elif command == 'ticker-perf' or command == 'tp':
        ticker = input("Ticker Codes (Space separated): ").strip()
        inv.tickerPerformance(ticker)

    elif command == 'value' or command == 'v':
        inv.listInvestments()
    
    elif command == 'history' or command == 'hs':
        inv.investmentHistory()

    elif command == 'dividend' or command == 'd':
        ticker = input('Ticker: ').strip()
        value = float(input('Value: $').strip())
        date = input('Date (DD-MM-YYYY): ').strip()
        inv.addDividend(date, ticker, value)

    elif command == 'estimate' or command == 'e':
        inv.estimateDividends()
    
    elif command == 'performance' or command == 'p':
        inv.stockPerformance()
    
    elif command == 'inv-perc' or command == 'ipc':
        inv.investmentPercentage()

    elif command == 'mkt-perc' or command == 'mpc':
        inv.marketPercentage()

    elif command == 'rebalance' or command == 'r':
        inv.rebalanceSuggestions()

    elif command == 'quit' or command == 'q':
        break

    else:
        print("Invalid command. Enter 'help' for list of commands.\n")
