import os
import json
import pandas as pd
import yfinance as yf

INVESTMENT_FILE_NAME = 'store/investments.json'
HISTORY_FILE_NAME = 'store/investment_history.json'
DIVIDEND_FILE = 'store/dividend_history.json'
PORTFOLIO_BALANCE_FILE = 'store/portfolio_balance.json'

# History File: tradeId:int, ticker:str, price:float, volume:int, brokerage:float, date:str
# Investment file: ticker, volume, cost, totalBrokerage, dividend
# Dividend file: dividendId, ticker, date, value
# Portfolio balance file: ticker: percentage


class Investments:
    def __init__(self):
        self.investments = self.getInvestments()
        self.history = self.getHistory()
        self.maxId = self.getMaxId()
        self.dividendHistory = self.getDividends()
        self.maxDividendId = self.getMaxDividendId()
        self.portfolioBalance = self.getPortfolioBalance()
    
    ###########
    # HELPERS #
    ###########

    def getHistory(self):
        """
        Get investment history from file
        """
        if os.path.isfile(HISTORY_FILE_NAME):
            with open(HISTORY_FILE_NAME, 'r') as f:
                return json.load(f)
        else:
            return {}
    
    def getInvestments(self):
        """
        Get investments from file
        """
        if os.path.isfile(INVESTMENT_FILE_NAME):
            with open(INVESTMENT_FILE_NAME, 'r') as f:
                return json.load(f)
        else:
            return {}
    
    def getDividends(self):
        """
        Get dividends from file
        """
        if os.path.isfile(DIVIDEND_FILE):
            with open(DIVIDEND_FILE, 'r') as f:
                return json.load(f)
        else:
            return {}
    
    def getPortfolioBalance(self):
        """
        Get portfolio balance from file
        """
        if os.path.isfile(PORTFOLIO_BALANCE_FILE):
            with open(PORTFOLIO_BALANCE_FILE, 'r') as f:
                return json.load(f)
        else:
            return {}

    def getMaxId(self):
        """
        Gets largest trade ID
        """
        if len(self.history.keys()) > 0:
            return max([int(tradeId) for tradeId in self.history])
        else:
            return 0
    
    def getMaxDividendId(self):
        """
        Gets largest trade ID
        """
        if len(self.dividendHistory.keys()) > 0:
            return max([int(dividendId) for dividendId in self.dividendHistory])
        else:
            return 0
    
    def getTickerData(self, tickers:str):
        """
        Get data for tickers from Yahoo Finance API
        Tickes space separated tickers in a string
        """

        tickerData = yf.Tickers(tickers)
        data = {}
        for ticker in tickers.split():
            # print(tickerData.tickers[ticker].info)
            data[ticker] = {}
            data[ticker]['price'] = tickerData.tickers[ticker].info['ask']
            data[ticker]['fullName'] = tickerData.tickers[ticker].info['longName']
            data[ticker]['yield'] = tickerData.tickers[ticker].info.get('yield', 0)
            data[ticker]['quoteType'] = tickerData.tickers[ticker].info['quoteType']
            data[ticker]['ytdReturn'] = tickerData.tickers[ticker].info.get('ytdReturn', None)
            data[ticker]['threeYrReturn'] = tickerData.tickers[ticker].info.get('threeYearAverageReturn', None)
            data[ticker]['fiveYrReturn'] = tickerData.tickers[ticker].info.get('fiveYearAverageReturn', None)

        return data
    
    def getTickerPrices(self, tickers:str):
        """
        Similar to `getTickerData` but only gets price
        Takes list of comma separated tickers
        """
        ticker_string = ' '.join(tickers)
        tickerData = yf.Tickers(ticker_string)
        data = {}
        for ticker in tickers:
            data[ticker] = tickerData.tickers[ticker].info['ask']

        return data

    def updateInvestmentFile(self):
        with open(INVESTMENT_FILE_NAME, 'w') as f:
            json.dump(self.investments, f)
            f.close()

    def updateHistoryFile(self):
        with open(HISTORY_FILE_NAME, 'w') as f:
            json.dump(self.history, f)
            f.close()
    
    def updateDividendFile(self):
        with open(DIVIDEND_FILE, 'w') as f:
            json.dump(self.dividendHistory, f)
            f.close()
    
    def updatePortfolioBalanceFile(self):
        with open(PORTFOLIO_BALANCE_FILE, 'w') as f:
            json.dump(self.portfolioBalance, f)
            f.close()

    def makeTickerString(self):
        """
        Produces a string of space separated tickers for use in yfinance lookup
        """
        # TODO: Add sort by date option
        
        tickersStr = ""
        tickers = [k for k, _ in sorted(self.investments.items(), key=lambda x:x[1]['cost'], reverse=True)]
        for ticker in tickers:
            tickersStr += f"{ticker} "
        return tickersStr.strip()


    def outputTickerHeader(self):
        print(f"\nTicker    {'Full Name'.ljust(60, ' ')}  Price    Cost      Value     %Gain    %NetGain  Gain      Net Gain  Dividends")
        print("-" * 9 + "+" + "-" * 61 + "+" + "-" * 8 + "+" + "-" * 9 + "+" + "-" * 9 + "+" + "-" * 8 + "+" + "-" * 9 + "+" + "-" * 9 + "+" + "-" * 9 + "+" + "-" * 9)


    def outputTickerValue(self, data:object, ticker:str):
        price = data[ticker]['price']
        fullName = data[ticker]['fullName']
        volume = self.investments[ticker]['volume']
        cost = self.investments[ticker]['cost']
        totalBrokerage = self.investments[ticker]['totalBrokerage']
        dividend = self.investments[ticker]['dividend']
        value = price * volume
        percGain = (value / (cost - totalBrokerage) - 1) * 100
        netPercGain = ((value + dividend) / cost - 1) * 100
        gain = value - (cost - totalBrokerage)
        netGain = value + dividend - cost

        print(f"{ticker.ljust(8, ' ')}  {fullName.ljust(60, ' ')}  {str(round(price, 2)).rjust(7, ' ')}  {str(round(cost, 2)).rjust(8, ' ')}  {str(round(value, 2)).rjust(8, ' ')}  {(str(round(percGain, 2)) + '%').rjust(7, ' ')}  {(str(round(netPercGain, 2)) + '%').rjust(7, ' ')}   {str(round(gain, 2)).rjust(8, ' ')}  {str(round(netGain, 2)).rjust(8, ' ')}  {str(round(dividend, 2)).rjust(7, ' ')}")

        return {'cost': cost, 'value': value, 'dividend': dividend, 'gain': gain, 'net_gain': netGain, 'brokerage': totalBrokerage}

    def printPortfolioBalanceTargets(self):
        print(f"\nTicker  Target")
        print("--------+------")
        for ticker in self.portfolioBalance:
            print(f"{ticker.ljust(8, ' ')} {(str(format(self.portfolioBalance[ticker], '.2f')) + '%').rjust(6, ' ')}")

    def updatePortfolioBalanceTargets(self):
        print('Provide ticker code and percentage.\n')

        balanceRows = {}
        percTotal = 0
        while percTotal < 100:
            ticker = input('Ticker: ').strip()
            targetPerc = 0
            while targetPerc <= 0:
                targetPerc = float(input(f'Current: {percTotal}%. Target percentage (%): ').strip())
                if targetPerc <= 0:
                    print('Error: Target percentage cannot be negative or 0.')
            percTotal += targetPerc
            balanceRows[ticker] = targetPerc

        if percTotal > 100:
            print('Error: Total percentage cannot exceed 100%.')
            return

        self.portfolioBalance = balanceRows
        self.updatePortfolioBalanceFile()

        print('\nCurrent Portfolio Balance Targets:')
        self.printPortfolioBalanceTargets()

    def sortByCost(x, y):
        if x['cost'] >= y['cost']:
            return x
        else:
            return y

    ###########
    # METHODS #
    ###########

    def buyInvestment(self, ticker:str, price:float, volume:int, brokerage:float, date:str):
        """
        Add investment to file and update investments
        """
        tradeId = int(self.maxId) + 1
        self.maxId = tradeId

        trade = {}
        trade['ticker'] = ticker
        trade['price'] = price
        trade['volume'] = volume
        trade['brokerage'] = brokerage
        trade['date'] = date
        trade['status'] = 'buy'

        self.history[tradeId] = trade
        self.updateHistoryFile()

        cost = volume * price + brokerage
        if ticker in self.investments.keys():
            self.investments[ticker]['volume'] += volume
            self.investments[ticker]['cost'] += cost
            self.investments[ticker]['totalBrokerage'] += brokerage
        else:
            self.investments[ticker] = {}
            self.investments[ticker]['volume'] = volume
            self.investments[ticker]['cost'] = cost
            self.investments[ticker]['totalBrokerage'] = brokerage
            self.investments[ticker]['dividend'] = 0
        
        self.updateInvestmentFile()

        print(f"Trade ID: {tradeId}. Purchased {volume} of {ticker} at ${price} per share on {date} with a ${brokerage} brokerage fee\n")
    

    def sellInvestment(self, tradeId:int, ticker:str, price:float, volume:int, brokerage:float, date:str):
        """
        Sell investment from file and update investments
        """
        allSold = False

        profit = volume * price - brokerage
        if ticker in self.investments.keys() and volume > self.investments[ticker]['volume']:
            self.investments[ticker]['volume'] -= volume
            self.investments[ticker]['cost'] -= profit
            self.investments[ticker]['totalBrokerage'] += brokerage
        elif ticker in self.investments.keys() and volume == self.investments[ticker]['volume']:
            self.investments.remove(ticker)
            allSold = True
        else:
            print("Error: invalid ticker or insufficient volume")

        self.updateInvestmentFile()

        trade = {}
        trade['ticker'] = ticker
        trade['price'] = price
        trade['volume'] = volume
        trade['brokerage'] = brokerage
        trade['date'] = date
        trade['status'] = 'sell'
        
        self.history[tradeId] = trade
        self.updateHistoryFile()


        print(f"Trade ID: {tradeId}. Sold {volume} of {ticker} at ${price} per share on {date} with a ${brokerage} brokerage fee\n")
        if allSold:
            print(f"-- All existing {volume} stock sold.\n")


    def listInvestments(self):
        """
        Output investments to command line sorted by value + do with and without dividends
        """

        # TODO: sort by value
    
        data = self.getTickerData(self.makeTickerString())

        self.outputTickerHeader()

        totalCost = 0
        totalValue = 0
        totalDividend = 0
        totalGain = 0
        totalNetGain = 0
        totalBrokerage = 0

        for ticker in data.keys():
            values = self.outputTickerValue(data, ticker)
            totalCost += values['cost']
            totalValue += values['value']
            totalDividend += values['dividend']
            totalGain += values['gain']
            totalNetGain += values['net_gain']
            totalBrokerage += values['brokerage']
        
        totalNetGain += totalDividend

        percGain = (totalValue / (totalCost - totalBrokerage) - 1) * 100
        netPercGain = (totalNetGain / totalCost) * 100
        print("-" * 149)
        print(f"          {'Total'.ljust(69, ' ')}  {str(round(totalCost, 2)).rjust(8, ' ')}  {str(round(totalValue, 2)).rjust(8, ' ')}  {(str(round(percGain, 2)) + '%').rjust(7, ' ')}  {(str(round(netPercGain, 2)) + '%').rjust(7, ' ')}   {str(round(totalGain, 2)).rjust(8, ' ')}  {str(round(totalNetGain, 2)).rjust(8, ' ')}  {str(round(totalDividend, 2)).rjust(7, ' ')}")
        print()


    def investmentValue(self, ticker:str):
        """
        Get value output for specific ticker + do with and without dividends
        """
        data = self.getTickerData(ticker)
        self.outputTickerHeader()
        self.outputTickerValue(data, ticker)
        print()
        
        # TODO: add invalid ticker error handling


    def investmentHistory(self):
        """
        Output investments or dividends to command line sorted by date
        """
        hsCommand = input('History type to display (trades/dividends): ').lower().strip()
        if hsCommand == 't' or hsCommand == 'trades':
            dfRows = []
            for invData in self.history.values():
                value = round(invData['price'] * invData['volume'], 2)
                dfRow = [invData['date'], invData['ticker'], invData['status'], value, invData['price'], invData['volume'], invData['brokerage']]
                dfRows.append(dfRow)
            
            histDF = pd.DataFrame(dfRows, columns = ['Date', 'Ticker', 'Status', 'Total Value', 'Price', 'Volume', 'Brokerage'])
            histDF['Date'] = pd.to_datetime(histDF['Date'], format='%d-%m-%Y')
            histDF = histDF.sort_values(by='Date')
            
            print(f'\n{histDF.to_string(index=False)}\n')
        elif hsCommand == 'd' or hsCommand == 'dividends':
            dfRows = []
            for divData in self.dividendHistory.values():
                dfRow = [divData['date'], divData['ticker'], divData['value']]
                dfRows.append(dfRow)
            
            histDF = pd.DataFrame(dfRows, columns = ['Date', 'Ticker', 'Value'])
            histDF['Date'] = pd.to_datetime(histDF['Date'], format='%d-%m-%Y')
            histDF = histDF.sort_values(by='Date')
            
            print(f'\n{histDF.to_string(index=False)}\n')
        else:
            print('Invalid history type specified.\n')


    def addDividend(self, date, ticker, value):
        """
        Add dividend received
        """
        if ticker not in self.investments.keys():
            print(f"Invalid ticker provided: {ticker}\n")
            return

        self.investments[ticker]['dividend'] += value
        self.updateInvestmentFile()

        dividendId = int(self.maxDividendId) + 1
        self.maxDividendId = dividendId

        dividend = {}
        dividend['ticker'] = ticker
        dividend['value'] = value
        dividend['date'] = date

        self.dividendHistory[dividendId] = dividend
        self.updateDividendFile()

        print(f"Recorded dividend receives for {ticker} on {date} at value of ${value}\n")
    

    def estimateDividends(self):
        """
        Estimated yearly dividends
        """
        data = self.getTickerData(self.makeTickerString())
        
        print(f"\nTicker    {'Full Name'.ljust(60, ' ')}  Value     Yield   Est. Return")
        print("-" * 9 + "+" + "-" * 61 + "+" + "-" * 9 + "+" + "-" * 7 + "+" + "-" * 11)

        totalReturn = 0
        sumYield = 0
        nTickers = 0
        totalValue = 0
        for ticker, info in data.items():
            yld = info['yield']
            volume = self.investments[ticker]['volume']
            price = info['price']
            fullName = info['fullName']

            value = volume * price
            estReturnPS = yld * price
            estReturn = estReturnPS * volume
            totalReturn += estReturn
            sumYield += yld
            nTickers += 1
            totalValue += value

            print(f"{ticker.ljust(8, ' ')}  {fullName.ljust(60, ' ')}  {str(round(value, 2)).rjust(8, ' ')}  {str(round(yld * 100, 3)).rjust(5, ' ')}%  {str(round(estReturn, 2)).rjust(11, ' ')}")

        avgYield = sumYield / nTickers

        print("-" * 101)
        print(f"          {'Total'.ljust(60, ' ')}  {str(round(totalValue, 2)).rjust(8, ' ')}  {str(round(avgYield * 100, 3)).rjust(5, ' ')}%  {str(round(totalReturn, 2)).rjust(11, ' ')}\n")


    def stockPerformance(self):
        """
        Output stock performance over YTD, 3Yrs, 5Yrs where available
        """
        # TODO: Change to sort by value

        data = self.getTickerData(self.makeTickerString())
        
        print(f"\nTicker    {'Full Name'.ljust(60, ' ')}  Value     YTD     3YR     5YR")
        print("-" * 9 + "+" + "-" * 61 + "+" + "-" * 9 + "+" + "-" * 7 + "+" + "-" * 7 + "+" + "-" * 7)

        sumYtd = 0
        sumThreeYrRet = 0
        sumFiveYrRet = 0
        nTickers = 0
        totalValue = 0

        for ticker, info in data.items():
            fullName = info['fullName']
            value = info['price'] * self.investments[ticker]['volume']
            ytd = info['ytdReturn']
            threeYrReturn = info['threeYrReturn']
            fiveYrReturn = info['fiveYrReturn']

            nTickers += 1
            totalValue += value
            
            if ytd:
                sumYtd += ytd
                ytd = str(round(ytd * 100, 2))
            else:
                ytd = '- '
            
            if threeYrReturn:
                sumThreeYrRet += threeYrReturn
                threeYrReturn = str(round(threeYrReturn * 100, 2))
            else:
                threeYrReturn = '- '
            
            if fiveYrReturn:
                sumFiveYrRet += fiveYrReturn
                fiveYrReturn = str(round(fiveYrReturn * 100, 2))
            else:
                fiveYrReturn = '- '

            print(f"{ticker.ljust(8, ' ')}  {fullName.ljust(60, ' ')}  {str(round(value, 2)).rjust(8, ' ')}  {ytd.rjust(5, ' ')}%  {threeYrReturn.rjust(5, ' ')}%  {fiveYrReturn.rjust(5, ' ')}%")

        avgYtd = str(round(sumYtd * 100 / nTickers, 2))
        avgThreeYrRet = str(round(sumThreeYrRet * 100 / nTickers, 2))
        avgFiveYrRet = str(round(sumFiveYrRet * 100 / nTickers, 2))

        print("-" * 100)
        print(f"          {'Total'.ljust(60, ' ')}  {str(round(totalValue, 2)).rjust(8, ' ')}  {avgYtd.rjust(5, ' ')}%  {avgThreeYrRet.rjust(5, ' ')}%  {avgFiveYrRet.rjust(5, ' ')}%\n")

    
    def investmentPercentage(self):
        data = self.getTickerData(self.makeTickerString())
        # totalValue = sum([x.values()['price'] * x.values()['volume'] for x in data])
        # totalCost = sum([x.values()['cost'] for x in data])
        

        print(f"\nTicker    {'Full Name'.ljust(60, ' ')}  Value     Cost      %Value    %Cost")
        print("-" * 9 + "+" + "-" * 61 + "+" + "-" * 9 + "+" + "-" * 9 + "+" + "-" * 9 + "+" + "-" * 9)
        
        nTickers = 0
        totalValue = 0
        totalCost = 0
        for ticker, info in data.items():
            value = info['price'] * self.investments[ticker]['volume']
            cost = self.investments[ticker]['cost']
            totalValue += value
            data[ticker]['value'] = value
            totalCost += cost
            data[ticker]['cost'] = cost
            nTickers += 1
        
        sortedTickers = [k for k, _ in sorted(data.items(), key=lambda x:x[1]['value'], reverse=True)]

        for ticker in sortedTickers:
            info = data[ticker]
            fullName = info['fullName']
            value = info['value']
            cost = info['cost']
            valuePrc = str(round((value / totalValue) * 100, 2))
            costPrc = str(round((cost / totalCost) * 100, 2))

            print(f"{ticker.ljust(8, ' ')}  {fullName.ljust(60, ' ')}  {str(round(value, 2)).rjust(8, ' ')}  {str(round(cost, 2)).rjust(8, ' ')}  {valuePrc.rjust(7, ' ')}%  {costPrc.rjust(7, ' ')}%")

        
        print("-" * 111)
        print(f"          {'Total'.ljust(60, ' ')}  {str(round(totalValue, 2)).rjust(8, ' ')}  {str(round(totalCost, 2)).rjust(8, ' ')}\n")


    def marketPercentage(self):
        print("To be implemented.\n")

    def rebalanceSuggestions(self):
        """
        Based on current portfolio value and ideal portfolio balance
        gives amounts needed for those investments to reach target balance.
        """
        if not self.portfolioBalance:
            print('\nTarget portfolio balance input required.')
            self.updatePortfolioBalanceTargets()

        else:
            print('\nCurrent Portfolio Balance Targets:')
            self.printPortfolioBalanceTargets()

            updateCmd = input('\nWould you like to update your targets (Y/N)? ').lower().strip()
            if updateCmd == 'y':
                self.updatePortfolioBalanceTargets()
            elif updateCmd != 'n':
                print('Invalid input received.')
                return
        
        prices = self.getTickerPrices(self.portfolioBalance.keys())
        data = {}
        
        totalValue = 0
        for ticker, price in prices.items():
            volume = self.investments[ticker]['volume']
            value = round(volume * price, 2)
            totalValue += value
            data[ticker] = {}
            data[ticker]['value'] = value
            data[ticker]['targetPerc'] = self.portfolioBalance[ticker]

        highestPercDiff = 0
        highestTicker = ""
        for ticker in data:
            currentPerc = (data[ticker]['value'] / totalValue) * 100
            data[ticker]['currentPerc'] = currentPerc
            targetPercDiff = (currentPerc - data[ticker]['targetPerc']) * (100 / data[ticker]['targetPerc'])
            if targetPercDiff > highestPercDiff:
                highestPercDiff = targetPercDiff
                highestTicker = ticker

        targetTotalValue = data[highestTicker]['value'] * (100 / data[highestTicker]['targetPerc'])

        dfRows = []
        for ticker in data:
            targetValue = targetTotalValue * (data[ticker]['targetPerc'] / 100)
            targetDiff = targetValue - data[ticker]['value']
            dfRows.append([
                ticker, 
                format(data[ticker]['currentPerc'], '.2f'), 
                format(data[ticker]['targetPerc'], '.2f'), 
                format(data[ticker]['value'], '.2f'), 
                format(targetValue, '.2f'), 
                format(targetDiff, '.2f')
            ])

        outputDf = pd.DataFrame(dfRows, columns=['Ticker', 'Current %', 'Target %', 'Value', 'Target Value', 'Suggestion'])
        print(f'\n{outputDf.to_string(index=False)}\n')
