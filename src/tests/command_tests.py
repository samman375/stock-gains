import unittest
from unittest.mock import patch, MagicMock
from prompt_toolkit.key_binding import KeyBindings

from commands.buy import buyInvestment
from commands.dividend import dividend
from commands.sell import sellInvestment

class TestCommands(unittest.TestCase):

    @patch('commands.buy.prompt')
    @patch('commands.buy.insertNewInvestmentHistory')
    @patch('commands.buy.addToPortfolio')
    def testBuyInvestment(self, mock_add, mock_insert, mock_prompt):
        mock_prompt.side_effect = ['AAPL', '150.0', '10', '5.0', '2023-10-10']
        mock_conn = MagicMock()
        mock_key_bindings = KeyBindings()

        buyInvestment(mock_conn, mock_key_bindings)

        mock_insert.assert_called_once_with(mock_conn, 'AAPL', 150.0, 10, 5.0, '2023-10-10', 'BUY')
        mock_add.assert_called_once_with(mock_conn, 'AAPL', 150.0, 10, 5.0)

        # Check if the connection was used in a transaction
        mock_conn.__enter__.assert_called_once()
        mock_conn.__exit__.assert_called_once()

    @patch('commands.sell.prompt')
    @patch('commands.sell.insertNewInvestmentHistory')
    @patch('commands.sell.reduceFromPortfolio')
    def testSellInvestment(self, mock_reduce, mock_insert, mock_prompt):
        mock_prompt.side_effect = ['AAPL', '150.0', '10', '5.0', '2023-10-10']
        mock_conn = MagicMock()
        mock_key_bindings = KeyBindings()

        sellInvestment(mock_conn, mock_key_bindings)

        mock_insert.assert_called_once_with(mock_conn, 'AAPL', 150.0, 10, 5.0, '2023-10-10', 'SELL')
        mock_reduce.assert_called_once_with(mock_conn, 'AAPL', 150.0, 10, 5.0)

        # Check if the connection was used in a transaction
        mock_conn.__enter__.assert_called_once()
        mock_conn.__exit__.assert_called_once()

    @patch('commands.dividend.prompt')
    @patch('commands.dividend.recordDividend')
    def testDividend(self, mock_record, mock_prompt):
        mock_prompt.side_effect = ['AAPL', '100.0', '2023-10-10']
        mock_conn = MagicMock()

        dividend(mock_conn)

        mock_record.assert_called_once_with(mock_conn, 'AAPL', 100.0, '2023-10-10')

if __name__ == '__main__':
    unittest.main()
