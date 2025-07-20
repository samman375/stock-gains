-- Schema for Dividends Table
CREATE TABLE IF NOT EXISTS dividends (
    ticker VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    distribution_value DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (ticker, date)
);

-- Schema for Investment History Table
CREATE TABLE IF NOT EXISTS investment_history (
    ticker VARCHAR(255) NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    volume INT NOT NULL,
    brokerage DOUBLE PRECISION NOT NULL,
    date DATE NOT NULL,
    status VARCHAR(10) NOT NULL CHECK (status IN ('BUY', 'SELL')),
    id SERIAL PRIMARY KEY
);

-- Schema for Target Portfolio Table
CREATE TABLE IF NOT EXISTS target_balance (
    bucket_tickers TEXT[] NOT NULL,
    percentage DOUBLE PRECISION NOT NULL CHECK (percentage >= 0 AND percentage <= 100),
    PRIMARY KEY (bucket_tickers)
);

CREATE TABLE IF NOT EXISTS settings (
    attribute VARCHAR(255) PRIMARY KEY,
    attribute_value TEXT NOT NULL
);

-- Add indexes to improve query performance
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'idx_dividends_date') THEN
        CREATE INDEX idx_dividends_date ON dividends (date);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'idx_investment_history_date') THEN
        CREATE INDEX idx_investment_history_date ON investment_history (date);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'idx_target_balance_percentage') THEN
        CREATE INDEX idx_target_balance_percentage ON target_balance (percentage);
    END IF;
END $$;

-- Create current portfolio view
DROP MATERIALIZED VIEW IF EXISTS current_portfolio;

CREATE MATERIALIZED VIEW current_portfolio AS
WITH buys AS (
    SELECT *
    FROM investment_history
    WHERE status = 'BUY'
),
sells AS (
    SELECT
        ticker,
        SUM(volume) AS total_sold
    FROM investment_history
    WHERE status = 'SELL'
    GROUP BY ticker
),
ordered_buys AS (
    SELECT *,
           volume AS original_volume,
           SUM(volume) OVER (
               PARTITION BY ticker
               ORDER BY price DESC, date ASC, id ASC
           ) AS cumulative_volume
    FROM buys
),
remaining AS (
    SELECT 
        b.ticker,
        b.price,
        GREATEST(0, b.volume - GREATEST(0, COALESCE(s.total_sold, 0) - (b.cumulative_volume - b.volume))) AS remaining_volume,
        b.volume AS original_volume
    FROM ordered_buys b
    LEFT JOIN sells s ON b.ticker = s.ticker
    WHERE COALESCE(s.total_sold, 0) < b.cumulative_volume
),
matched_sales AS (
    SELECT
        b.ticker,
        b.price AS buy_price,
        LEAST(
            b.original_volume,
            GREATEST(0, COALESCE(s.total_sold, 0) - (b.cumulative_volume - b.original_volume))
        ) AS sold_volume
    FROM ordered_buys b
    LEFT JOIN sells s ON b.ticker = s.ticker
    WHERE COALESCE(s.total_sold, 0) > (b.cumulative_volume - b.original_volume)
),
avg_sell_prices AS (
    SELECT
        ticker,
        SUM(volume * price)::numeric / SUM(volume) AS avg_sell_price
    FROM investment_history
    WHERE status = 'SELL'
    GROUP BY ticker
),
realized_profits AS (
    SELECT
        m.ticker,
        ROUND(SUM(m.sold_volume * (s.avg_sell_price - m.buy_price))::numeric, 2) AS realized_profit
    FROM matched_sales m
    JOIN avg_sell_prices s ON m.ticker = s.ticker
    GROUP BY m.ticker
),
aggregated AS (
    SELECT
        r.ticker,
        SUM(r.remaining_volume) AS total_volume,
        ROUND(SUM(r.remaining_volume * r.price)::numeric / NULLIF(SUM(r.remaining_volume), 0), 2) AS average_price
    FROM remaining r
    GROUP BY r.ticker
),
buy_brokerage_totals AS (
    SELECT
        ticker,
        ROUND(SUM(brokerage)::numeric, 2) AS buy_brokerage
    FROM investment_history
    WHERE status = 'BUY'
    GROUP BY ticker
),
sell_brokerage_totals AS (
    SELECT
        ticker,
        ROUND(SUM(brokerage)::numeric, 2) AS sell_brokerage
    FROM investment_history
    WHERE status = 'SELL'
    GROUP BY ticker
)
SELECT
    a.ticker,
    a.total_volume,
    a.average_price,
    COALESCE(p.realized_profit, 0) AS realized_profit,
    COALESCE(bb.buy_brokerage, 0) AS buy_brokerage,
    COALESCE(sb.sell_brokerage, 0) AS sell_brokerage
FROM aggregated a
LEFT JOIN realized_profits p ON a.ticker = p.ticker
LEFT JOIN buy_brokerage_totals bb ON a.ticker = bb.ticker
LEFT JOIN sell_brokerage_totals sb ON a.ticker = sb.ticker
UNION
SELECT
    p.ticker,
    0 AS total_volume,
    NULL::numeric AS average_price,
    p.realized_profit,
    COALESCE(bb.buy_brokerage, 0) AS buy_brokerage,
    COALESCE(sb.sell_brokerage, 0) AS sell_brokerage
FROM realized_profits p
LEFT JOIN buy_brokerage_totals bb ON p.ticker = bb.ticker
LEFT JOIN sell_brokerage_totals sb ON p.ticker = sb.ticker
WHERE NOT EXISTS (
    SELECT 1 FROM aggregated a WHERE a.ticker = p.ticker
);
