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
