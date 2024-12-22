import re
from prompt_toolkit.validation import Validator, ValidationError

from db.crud import checkIfTickerExists
from requests.yfinance_fetcher import isValidTicker

class NonNegativeFloatValidator(Validator):
    def validate(self, document):
        try:
            value = float(document.text)
            if value < 0:
                raise ValidationError(message='The value cannot be less than 0', cursor_position=len(document.text))
        except ValueError:
            raise ValidationError(message='This input contains non-numeric characters', cursor_position=len(document.text))

class NonNegativeIntValidator(Validator):
    def validate(self, document):
        if not document.text.isdigit():
            raise ValidationError(message='This input contains non-numeric characters', cursor_position=len(document.text))
        value = int(document.text)
        if value < 0:
            raise ValidationError(message='The value cannot be less than 0', cursor_position=len(document.text))

class DateValidator(Validator):
    def validate(self, document):
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        if not date_pattern.match(document.text):
            raise ValidationError(message='Invalid date format. Use YYYY-MM-DD.', cursor_position=len(document.text))

class TickerValidator(Validator):
    """
    Checks if a provided ticker exists in database or is valid in yfinance
    """
    def __init__(self, conn):
        self.conn = conn

    def validate(self, document):
        ticker = document.text
        if not checkIfTickerExists(self.conn, ticker) or not isValidTicker(ticker):
            raise ValidationError(message='Invalid ticker provided. Use only letters.', cursor_position=len(ticker))
