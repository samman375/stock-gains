# Refactor Design

Written by samman375, December 2024

## Requirements
- Improve startup performance
    - Remove use of csv files
- Retain ease of data storage without any operations costs that come with cloud deployments
- Implement auto backup of data
    - give user option to restore from backup
- Improve code readability
    - breakup files + introduce directory hierachies
- Standardise data display across functions
    - enforce pandas output usage
- improve user command interaction experience
    - utilise cmd/prompt_toolkit libraries

## Data Storage Solution

- Utilise Postgres database
- Backups stored in iCloud
- When user runs quit program command, data is backed up
    - Could keep up to 3 backups?
- Program can load most recent backup on start

### Database Design

#### Dividends

- Table name: dividends
- Columns:
    - Ticker (string)
    - Value (double)
    - Date (ISO_LOCAL_DATE)

#### Investments

- Table name: investment_history
- Columns:
    - Ticker (string)
    - Price (double)
    - Volume (int)
    - Brokerage (double)
    - Date (ISO_LOCAL_DATE)
    - Status (String eg. BUY/SELL)

#### Target Portfolio

- Table name: target_balance
- Columns:
    - Bucket Tickers (string)
    - Percentage (double)

#### Portfolio Cache

- Table name: current_investments
- Columns:
    - Ticker (string)
    - Cost (double)
    - Total Brokerage (double)
    - Dividends (double)

## Hierarchy Redesign

- src/
    - commands/
        - (All app commands go here)
    - db/
        - db_handler.py         (contains db setup logic/interaction)
        - crud.py               (contains all queries)
        - backup_handler.py     (read/write to backups)
        - config.py             (contains db setup variables)
        - schema.sql            (contaisn table creation schemas)
        - migrations/           (for future schema migrations)
    - requests/
        - yfinance_fetcher.py   (contains yfinance interactions)
    - utils/
        - (All helper logic goes here)
        - validation.py         (contains input validation functions)
    - stock_gains.py (main)
- tests/
- README.md
