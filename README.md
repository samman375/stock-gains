# stock-gains

A free command-line portfolio tracking tool, that also does not store and on-sell personal data to our government and corporate overlords.

Disclaimer: 
- This tool was created and designed with the 'buy and hold' investment strategy in mind. The data storage methods were not chosen with a very large number of investments in mind.
- Live data is gathered from the `yfinance` library, which scapes Yahoo finance. As a result accuracy of data cannot be guaranteed.
- No liability is claimed by the creators in the case of financial loss as a result of reliance in this tool.

See open issues for future features and bugs.

## Usage

To run program:
```sh
pip install pandas yfinance
python3 gains.py
```

Entering `help` as the command when prompted will return a full list of available command.

Investment history must currently be implemented manually using the `buy` command. Scraping of a order history file as input is planned
as a future feature.

Data is stored locally in `/store` as a free solution and to avoid maintaining an active database connection.

### Recommended:

The following can be added to your shell configuration file (such as `~/.zshrc`) to allow easy access from anywhere, replacing `PATH_TO_LIBRARY`:
```sh
# stock-gains
alias stock-gains="cd PATH_TO_LIBRARY && python3 gains.py && cd - >/dev/null"
```

The program can then be run from any subdirectory with:
```sh
stock-gains
```
