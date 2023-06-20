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
        'hs' or 'history':      Investment history
        'd' or 'dividend':      Add received dividend
        'e' or 'estimate':      Get dividend estimate for next 12 months
        'p' or 'performance':   Get historical stock performance
        'h' or 'help':          Help
        'q' or 'quit':          Quit
        """
        print(help)

    elif command == 'buy' or command == 'b':
        ticker = input('Ticker: ').strip()
        price = float(input('Price: ').strip())
        volume = int(input('Volume: ').strip())
        brokerage = float(input('Brokerage: ').strip())
        date = input('Date (DD-MM-YYYY): ').strip()
        inv.buyInvestment(ticker, price, volume, brokerage, date)

    elif command == 'sell' or command == 's':
        continue

    elif command == 'ticker-value' or command == 't':
        ticker = input("Ticker Code: ").strip()
        inv.investmentValue(ticker)

    elif command == 'value' or command == 'v':
        inv.listInvestments()
    
    elif command == 'history' or command == 'h':
        continue

    elif command == 'dividend' or command == 'd':
        continue

    elif command == 'estimate' or command == 'e':
        inv.estimateDividends()
    
    elif command == 'performance' or command == 'p':
        inv.stockPerformance()

    elif command == 'quit' or command == 'q':
        break

    else:
        print("Invalid command. Enter 'help' for list of commands.")
