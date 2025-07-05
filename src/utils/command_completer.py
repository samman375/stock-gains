from prompt_toolkit.completion import NestedCompleter

COMMANDS = NestedCompleter.from_nested_dict({
    "value": {
        "--full": None,             # Add full output option
    },
    "buy": None,
    "sell": None,
    "dividend": None,               # Add dividend estimate
    # "ammend": None,               # decide how to do dividend vs buy/sale ammend
    "historical-performance": {     # historical performance of all owned tickers
        "--ticker": None,           # historical performance of specific ticker
    },
    "investment-history": None,
    "portfolio-balance": None,      # Add market percentage
    "rebalance-suggestions": None,
    "settings": None,               # Add backup location, restore backup
    "help": None,                   # Auto-generated?
    "quit": None
})

COMMAND_DESCRIPTIONS = {
    "value": "Show portfolio value summary",
    # "--full": "Show full details in value output",
    "buy": "Record a new investment purchase",
    "sell": "Record a sale of an investment",
    "dividend": "Record a dividend payment",
    "investment-history": "Show trade or dividend investment history",
    "historical-performance": "Show historical performance of current investments",
    # "--ticker": "Show historical performance of specific ticker",
    "rebalance-suggestions": "Suggest portfolio rebalancing",
    "portfolio-balance": "Show exposure balances of current portfolio",
    "ammend": "Amend a trade or dividend entry",
    "settings": "Configure application settings",
}
