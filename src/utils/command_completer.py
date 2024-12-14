from prompt_toolkit.completion import NestedCompleter

COMMANDS = NestedCompleter.from_nested_dict({
    "value": {
        "--ticker": None
    },
    "buy": None,
    "sell": None,
    "dividend": None,               # Add dividend estimate
    # "ammend": None,               # decide how to do dividend vs buy/sale ammend
    "historical-performance": None, # Add ticker perf
    "investment-history": None,
    "portfolio-balance": None,      # Add market percentage
    "rebalance-suggestions": None,
    # "settings": None,             # Add backup location, restore backup
    # "help": None                  # Auto-generated?
    "quit": None
})
