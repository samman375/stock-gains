import unittest
from unittest.mock import patch, MagicMock

from db.crud import (
    getDistinctTickers, 
    checkIfTickerExists,
    getCurrentPortfolioTickerData,
    insertNewInvestmentHistory,
    addToPortfolio,
    reduceFromPortfolio,
    recordDividend
)
import db.queries as q

# TODO: Fix these. Queries were modified to not take params

class TestCrudFunctions(unittest.TestCase):

    @patch('db.crud.psycopg2.connect')
    def testGetDistinctTickers(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [('AAPL'), ('GOOGL'), ('MSFT')]

        tickers = getDistinctTickers(mock_conn)

        mock_cursor.execute.assert_called_once_with(q.distinctTickersQuery())

        self.assertEqual(tickers, ['AAPL', 'GOOGL', 'MSFT'])

    @patch('db.crud.psycopg2.connect')
    def testCheckIfTickerExists(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ('AAPL')

        exists = checkIfTickerExists(mock_conn, 'AAPL')

        self.assertTrue(exists)

        # Test when ticker does not exist
        mock_cursor.fetchone.return_value = None
        exists = checkIfTickerExists(mock_conn, 'TSLA')
        self.assertFalse(exists)

    @patch('db.crud.psycopg2.connect')
    def testGetCurrentPortfolioTickerData(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ('AAPL', 500, 10, 50, 5)

        ticker_data = getCurrentPortfolioTickerData(mock_conn, 'AAPL')

        mock_cursor.execute.assert_called_once_with(q.currentPortfolioTickerQuery('AAPL'))

        expected_data = {
            'ticker': 'AAPL',
            'cost': 500,
            'volume': 10,
            'total_brokerage': 50,
            'dividends': 5
        }
        self.assertEqual(ticker_data, expected_data)

    # TODO: Fix these tests. Could be failing due to transaction management

    # @patch('db.crud.psycopg2.connect')
    # def testInsertNewInvestmentHistory(self, mock_connect):
    #     mock_conn = MagicMock()
    #     mock_cursor = MagicMock()
    #     mock_connect.return_value = mock_conn
    #     mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    #     insertNewInvestmentHistory(mock_conn, 'AAPL', 150.0, 10, 5.0, '2023-10-10', 'BUY')

    #     mock_cursor.execute.assert_called_once_with(q.investmentHistoryInsert('AAPL', 150.0, 10, 5.0, '2023-10-10', 'BUY'))
    #     mock_cursor.close.assert_called_once()

    # @patch('db.crud.checkIfTickerExists')
    # @patch('db.crud.psycopg2.connect')
    # def testAddToPortfolio(self, mock_connect, mock_check):
    #     mock_conn = MagicMock()
    #     mock_cursor = MagicMock()
    #     mock_connect.return_value = mock_conn
    #     mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    #     mock_check.return_value = True

    #     with mock_conn:
    #         addToPortfolio(mock_conn, 'AAPL', 150.0, 10, 5.0)

    #     print(f"Called execute with: {mock_cursor.execute.call_args_list}")

    #     # Verify that the mock cursor's execute method was called
    #     self.assertTrue(mock_cursor.execute.called, "The execute method was not called on the mock cursor")

    #     mock_cursor.execute.assert_called_once_with(q.currentPortfolioBuyUpdate(1500.0 + 5.0, 5.0, 10, 'AAPL'))

    #     # Test the insert case
    #     mock_check.return_value = False
    #     with mock_conn:
    #         addToPortfolio(mock_conn, 'AAPL', 150.0, 10, 5.0)
    #     mock_cursor.execute.assert_called_with(q.currentPortfolioInsert('AAPL', 1500.0 + 5.0, 5.0, 10))

    #     mock_cursor.close.assert_called()

    # @patch('db.crud.checkIfTickerExists')
    # @patch('db.crud.psycopg2.connect')
    # def testReduceFromPortfolio(self, mock_connect, mock_check):
    #     mock_conn = MagicMock()
    #     mock_cursor = MagicMock()
    #     mock_connect.return_value = mock_conn
    #     mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    #     mock_check.return_value = True

    #     reduceFromPortfolio(mock_conn, 'AAPL', 150.0, 10, 5.0)

    #     mock_cursor.execute.assert_any_call(q.currentPortfolioSellUpdate(1500.0 - 5.0, 5.0, 10, 'AAPL'))

    #     # Check if the cursor's execute method was called with the correct SQL for deleting if volume is 0 or less
    #     mock_cursor.execute.assert_any_call(q.currentPortfolioDeleteIfZero('AAPL'))

    #     # Test the case where the ticker does not exist
    #     mock_check.return_value = False
    #     with self.assertRaises(Exception) as context:
    #         reduceFromPortfolio(mock_conn, 'AAPL', 150.0, 10, 5.0)
    #     self.assertTrue('Ticker AAPL does not exist in portfolio. Nothing to sell' in str(context.exception))

    #     mock_cursor.close.assert_called()

    @patch('db.crud.psycopg2.connect')
    def testRecordDividend(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        recordDividend(mock_conn, 'AAPL', 100.0, '2023-10-10')

        mock_cursor.execute.assert_called_once_with(q.dividendsInsert('AAPL', '2023-10-10', 100.0))

if __name__ == '__main__':
    unittest.main()
