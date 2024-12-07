-- Schema for Dividends Table
CREATE TABLE dividends (
    ticker VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (ticker, date)
);

-- Schema for Investment History Table
CREATE TABLE investment_history (
    ticker VARCHAR(255) NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    volume INT NOT NULL,
    brokerage DOUBLE PRECISION NOT NULL,
    date DATE NOT NULL,
    status VARCHAR(10) NOT NULL CHECK (status IN ('BUY', 'SELL')),
    id SERIAL PRIMARY KEY
);

-- Schema for Target Portfolio Table
CREATE TABLE target_balance (
    bucket_tickers VARCHAR(255) NOT NULL,
    percentage DOUBLE PRECISION NOT NULL CHECK (percentage >= 0 AND percentage <= 100),
    PRIMARY KEY (bucket_tickers)
);

-- Schema for Portfolio Cache Table
CREATE TABLE current_investments (
    ticker VARCHAR(255) NOT NULL,
    cost DOUBLE PRECISION NOT NULL,
    total_brokerage DOUBLE PRECISION NOT NULL,
    dividends DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (ticker)
);

-- Add indexes to improve query performance
CREATE INDEX idx_dividends_date ON dividends (date);
CREATE INDEX idx_investment_history_date ON investment_history (date);
CREATE INDEX idx_target_balance_percentage ON target_balance (percentage);
CREATE INDEX idx_current_investments_cost ON current_investments (cost);
