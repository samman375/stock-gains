import re
from prompt_toolkit.validation import Validator, ValidationError

from db.crud import checkIfTickerExists
from fetchers.yfinance_fetcher import isValidYfinanceTicker

YES_TEXT = ['y', 'yes']
NO_TEXT = ['n', 'no']

def isNonNegative(value):
    return value >= 0

def isValidDate(date):
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    return date_pattern.match(date)

def isValidExistingTicker(conn, ticker):
    return checkIfTickerExists(conn, ticker)

def isValidTicker(conn, ticker):
    return isValidExistingTicker(conn, ticker) or isValidYfinanceTicker(ticker)

class BooleanValidator(Validator):
    def validate(self, document):
        if not document.text.lower().strip() in ['y', 'yes', 'n', 'no']:
            raise ValidationError(message='Please enter "Y" or "N".', cursor_position=len(document.text))

class NonNegativeFloatValidator(Validator):
    def validate(self, document):
        try:
            value = float(document.text)
            if not isNonNegative(value):
                raise ValidationError(message='The value cannot be less than 0', cursor_position=len(document.text))
        except ValueError:
            raise ValidationError(message='This input contains non-numeric characters', cursor_position=len(document.text))

class NonNegativeIntValidator(Validator):
    def validate(self, document):
        if not document.text.isdigit():
            raise ValidationError(message='This input contains non-numeric characters', cursor_position=len(document.text))
        value = int(document.text)
        if not isNonNegative(value):
            raise ValidationError(message='The value cannot be less than 0', cursor_position=len(document.text))

class DateValidator(Validator):
    def validate(self, document):
        if not isValidDate(document.text):
            raise ValidationError(message='Invalid date format. Use YYYY-MM-DD.', cursor_position=len(document.text))

class ExistingTickerValidator(Validator):
    """
    Checks if a provided ticker exists in database
    """
    def __init__(self, conn):
        self.conn = conn

    def validate(self, document):
        ticker = document.text
        if not isValidExistingTicker(self.conn, ticker):
            raise ValidationError(message='Ticker does not exist in database.', cursor_position=len(ticker))

class TickerValidator(Validator):
    """
    Checks if a provided ticker exists in database or is valid in yfinance
    """
    def __init__(self, conn):
        self.conn = conn

    def validate(self, document):
        ticker = document.text
        if not isValidTicker(self.conn, ticker):
            raise ValidationError(message='Invalid ticker provided.', cursor_position=len(ticker))

class SettingBooleanValidator(Validator):
    """
    Validates boolean setting values (true/false only, case-insensitive)
    """
    def validate(self, document):
        value = document.text.lower().strip()
        if value and value not in ['true', 'false']:
            raise ValidationError(message='Boolean setting must be: true or false', cursor_position=len(document.text))

class SettingJsonValidator(Validator):
    """
    Validates that input is valid JSON (specifically a Python list representation)
    """
    def validate(self, document):
        text = document.text.strip()
        if text:
            try:
                import ast
                ast.literal_eval(text)
            except (ValueError, SyntaxError):
                raise ValidationError(
                    message="Invalid JSON or Python list format",
                    cursor_position=len(document.text)
                )
