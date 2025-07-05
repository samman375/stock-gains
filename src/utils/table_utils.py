def formatCurrency(value):
    num = float(value)
    if num < 0:
        return f"-${abs(num):,.2f}"
    else:
        return f"${num:,.2f}"

def formatPercentage(value):
    if value is None or value == "N/A":
        return "-"
    return f"{value:.2f}%"

def formatPeRatio(value):
    if value is None or value == "N/A":
        return "-"
    return f"{value:.2f}"

def formatTickerGroup(tickerGroup):
    if not tickerGroup:
        return "-"
    if isinstance(tickerGroup, list):
        return ', '.join(tickerGroup)
    return tickerGroup
