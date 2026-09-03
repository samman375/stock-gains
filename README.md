# stock-gains

A free command-line portfolio tracking tool, that also does not store and on-sell personal data to our government and corporate overlords.

Disclaimer: 
- This tool was created and designed with the 'buy and hold' investment strategy in mind.
- Live data is gathered from the `yfinance` library, which scrapes Yahoo finance. As a result accuracy of data cannot be guaranteed.
- No liability is claimed by the creators in the case of financial loss as a result of reliance in this tool.

See open issues for future features and bugs.

## Installation & Usage

To install clone this repository in a suitable location, then:
```sh
cd stock-gains
pip install .
```

Then run from any directory:
```sh
stock-gains
```

To see the list of available commands use `help`.

## Example commands and functionality

Once the app is running, you can use the interactive prompt to track and review your portfolio.

```text
stock-gains
Enter command: help
Enter command: value
Enter command: value --full
Enter command: buy
Enter command: sell
Enter command: dividend
Enter command: investment-history
Enter command: investment-history --ticker AAPL
Enter command: investment-performance
Enter command: index-performance
Enter command: rebalance-suggestions
Enter command: fear-and-greed
Enter command: settings
Enter command: quit
```

Overview of the main features:

- `value` and `value --full`: show your current portfolio value with optional fuller details.
- `buy`, `sell`, and `dividend`: record transactions and dividend activity.
- `investment-history`: review your trade and dividend history, optionally filtered by ticker.
- `investment-performance`: analyse performance for your current investments.
- `index-performance`: compare your portfolio against common market indices.
- `rebalance-suggestions`: get guidance on portfolio balancing.
- `fear-and-greed`: fetch the current market sentiment indicator.
- `settings`: configure app settings and backups.

### \[Optional\] Adding executable to PATH for autocompletion in terminal

Add the following line to your `~/.zshrc` file or equiavalent depending on your default shell:
```sh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc'
```

## Tests

To run tests:
```sh
python -m unittest -v tests.crud_tests
python -m unittest -v tests.command_tests
```
