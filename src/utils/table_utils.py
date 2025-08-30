import re

def formatCurrency(value, includeDollarSign=True, decimal_places=2):
    # Convert scientific notation to float if needed
    if isinstance(value, str) and re.search(r'e[-+]?\d+', value, re.IGNORECASE):
        try:
            num = float(value)
        except ValueError:
            return value
    else:
        num = float(value)

    fmt = f",.{decimal_places}f"
    if includeDollarSign:
        if num < 0:
            return f"-${abs(num):{fmt}}"
        else:
            return f"${num:{fmt}}"
    else:
        if num < 0:
            return f"-{abs(num):{fmt}}"
        else:
            return f"{num:{fmt}}"

def formatPercentage(value):
    if value is None or value == "N/A":
        return "-"
    return f"{value:.2f}%"

def formatRatio(value):
    if value is None or value == "N/A":
        return "-"
    return f"{value:.2f}"

def formatTickerGroup(tickerGroup):
    if not tickerGroup:
        return "-"
    if isinstance(tickerGroup, list):
        return ', '.join(tickerGroup)
    return tickerGroup
