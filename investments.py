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
    
    def getNextTradeID(self):
        """
        Gets the next trade ID
        """
        return int(self.maxId) + 1
    
    def getMaxDividendId(self):
        """
        Gets largest dividend ID
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
            data[ticker] = {
                'price': tickerData.tickers[ticker].info['ask'],
                'fullName': tickerData.tickers[ticker].info['longName'],
                'yield': tickerData.tickers[ticker].info.get('yield', 0),
                'quoteType': tickerData.tickers[ticker].info['quoteType'],
                'peRatio': tickerData.tickers[ticker].info.get('trailingPE', None),
                'volume': tickerData.tickers[ticker].info['volume'],
                'ytdReturn': tickerData.tickers[ticker].info.get('ytdReturn', None),
                'threeYrReturn': tickerData.tickers[ticker].info.get('threeYearAverageReturn', None),
                'fiveYrReturn': tickerData.tickers[ticker].info.get('fiveYearAverageReturn', None)
            }

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

        print(f"{ticker.ljust(8, ' ')}  {fullName.ljust(60, ' ')}  {str('%.2f' % price).rjust(7, ' ')}  {str('%.2f' % cost).rjust(8, ' ')}  {str('%.2f' % value).rjust(8, ' ')}  {(str('%.2f' % percGain) + '%').rjust(7, ' ')}  {(str('%.2f' % netPercGain) + '%').rjust(7, ' ')}   {str('%.2f' % gain).rjust(8, ' ')}  {str('%.2f' % netGain).rjust(8, ' ')}  {str('%.2f' % dividend).rjust(7, ' ')}")

        return {'cost': cost, 'value': value, 'dividend': dividend, 'gain': gain, 'net_gain': netGain, 'brokerage': totalBrokerage}

    def printPortfolioBalanceTargets(self):
        df = pd.DataFrame(self.portfolioBalance.items(), columns=['Ticker Group', 'Target %'])
        print(f'\n{df.to_string(index=False)}\n')

    def updatePortfolioBalanceTargets(self):
        print('Provide ticker code and percentage.')
        print('To combine tickers separate using a `+`, such as: NDQ.AX+IVV.AX\n')

        balanceRows = {}
        percTotal = 0
        while percTotal < 100:
            ticker = input('Ticker: ').strip()  # TODO: Add instructions on combining
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
        tradeId = self.getNextTradeID()
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

        print(f"Trade ID: {tradeId}. Purchased {volume} of {ticker} at ${price} per share on {date} with a ${brokerage} brokerage fee. Trade value: ${cost}\n")
    

    def sellInvestment(self, ticker:str, price:float, volume:int, brokerage:float, date:str):
        """
        Sell investment from file and update investments
        """
        tradeId = self.getNextTradeID()
        self.maxId = tradeId

        allSold = False

        profit = volume * price - brokerage
        if ticker in self.investments.keys() and volume > self.investments[ticker]['volume']:
            self.investments[ticker]['volume'] -= volume
            self.investments[ticker]['cost'] -= profit
            self.investments[ticker]['totalBrokerage'] += brokerage
        elif ticker in self.investments.keys() and volume == self.investments[ticker]['volume']:
            try:
                self.investments.pop(ticker)
            except KeyError:
                print("Error: invalid ticker")
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

        print(f"Trade ID: {tradeId}. Sold {volume} of {ticker} at ${price} per share on {date} with a ${brokerage} brokerage fee. Trade value: ${profit}\n")
        if allSold:
            print(f"-- All existing {volume} stock sold. --\n")


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
        print(f"          {'Total'.ljust(69, ' ')}  {str('%.2f' % totalCost).rjust(8, ' ')}  {str('%.2f' % totalValue).rjust(8, ' ')}  {(str('%.2f' % percGain) + '%').rjust(7, ' ')}  {(str('%.2f' % netPercGain) + '%').rjust(7, ' ')}   {str('%.2f' % totalGain).rjust(8, ' ')}  {str('%.2f' % totalNetGain).rjust(8, ' ')}  {str('%.2f' % totalDividend).rjust(7, ' ')}")
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

            print(f"{ticker.ljust(8, ' ')}  {fullName.ljust(60, ' ')}  {str('%.2f' % value).rjust(8, ' ')}  {str('%.2f' % (yld * 100)).rjust(5, ' ')}%  {str('%.2f' % estReturn).rjust(11, ' ')}")

        avgYield = sumYield / nTickers

        print("-" * 101)
        print(f"          {'Total'.ljust(60, ' ')}  {str('%.2f' % totalValue).rjust(8, ' ')}  {str('%.2f' % (avgYield * 100)).rjust(5, ' ')}%  {str('%.2f' % totalReturn).rjust(11, ' ')}\n")


    def stockPerformance(self):
        """
        Output stock performance over YTD, 3Yrs, 5Yrs where available
        """
        # TODO: Change to sort by value

        data = self.getTickerData(self.makeTickerString())
        
        print(f"\nTicker    {'Full Name'.ljust(60, ' ')}  Value     YTD      3YR      5YR      PE Ratio  Volume")
        print("-" * 9 + "+" + "-" * 61 + "+" + "-" * 9 + "+" + "-" * 8 + "+" + "-" * 8 + "+" + "-" * 8 + "+" + "-" * 9 + "+" + "-" * 7)

        sumYtd = 0
        sumThreeYrRet = 0
        sumFiveYrRet = 0
        nTickers = 0
        totalValue = 0
        totalPeRatio = 0
        totalPeRatioValue = 0
        totalVolume = 0

        for ticker, info in data.items():
            fullName = info['fullName']
            value = info['price'] * self.investments[ticker]['volume']
            ytd = info['ytdReturn']
            threeYrReturn = info['threeYrReturn']
            fiveYrReturn = info['fiveYrReturn']
            peRatio = info['peRatio']
            volume = info['volume']

            nTickers += 1
            totalValue += value
            totalVolume += volume * value
            
            if ytd:
                sumYtd += ytd
                ytd = str("%.2f" % (ytd * 100))
            else:
                ytd = '- '
            
            if threeYrReturn:
                sumThreeYrRet += threeYrReturn
                threeYrReturn = str("%.2f" % (threeYrReturn * 100))
            else:
                threeYrReturn = '- '
            
            if fiveYrReturn:
                sumFiveYrRet += fiveYrReturn
                fiveYrReturn = str("%.2f" % (fiveYrReturn * 100))
            else:
                fiveYrReturn = '- '
            
            if peRatio:
                totalPeRatio += peRatio * value
                totalPeRatioValue += value
                peRatio = str("%.2f" % peRatio)
            else:
                peRatio = '- '

            print(f"{ticker.ljust(8, ' ')}  {fullName.ljust(60, ' ')}  {str('%.2f' % value).rjust(8, ' ')}  {ytd.rjust(6, ' ')}%  {threeYrReturn.rjust(6, ' ')}%  {fiveYrReturn.rjust(6, ' ')}%     {peRatio.rjust(5, ' ')}  {str(volume).rjust(7, ' ')}")

        avgYtd = str("%.2f" % (sumYtd * 100 / nTickers))
        avgThreeYrRet = str("%.2f" % (sumThreeYrRet * 100 / nTickers))
        avgFiveYrRet = str("%.2f" % (sumFiveYrRet * 100 / nTickers))
        avgPeRatio = str("%.2f" % (totalPeRatio / totalPeRatioValue))
        avgVolume = str(round(totalVolume / totalValue))

        print("-" * 126)
        print(f"          {'Total'.ljust(60, ' ')}  {str('%.2f' % totalValue).rjust(8, ' ')}  {avgYtd.rjust(6, ' ')}%  {avgThreeYrRet.rjust(6, ' ')}%  {avgFiveYrRet.rjust(6, ' ')}%     {avgPeRatio.rjust(5, ' ')}  {avgVolume.rjust(7, ' ')}\n")

    
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
            valuePrc = str('%.2f' % ((value / totalValue) * 100))
            costPrc = str('%.2f' % ((cost / totalCost) * 100))

            print(f"{ticker.ljust(8, ' ')}  {fullName.ljust(60, ' ')}  {str('%.2f' % value).rjust(8, ' ')}  {str('%.2f' % cost).rjust(8, ' ')}  {valuePrc.rjust(7, ' ')}%  {costPrc.rjust(7, ' ')}%")

        
        print("-" * 111)
        print(f"          {'Total'.ljust(60, ' ')}  {str('%.2f' % totalValue).rjust(8, ' ')}  {str('%.2f' % totalCost).rjust(8, ' ')}\n")


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
                print('Invalid input received.\n')
                return

        targetTotalValue = 0
        userHasTargetValue = input('Do you have a total portfolio target in mind (Y/N)? ').lower().strip()
        if userHasTargetValue == 'y':
            while targetTotalValue <= 0:
                targetTotalValue = float(input('Enter target value: $').strip())
                if targetTotalValue <= 0:
                    print('Invalid target received. Target must be greater than $0.')
        elif userHasTargetValue != 'n':
            print('Invalid input received.\n')
            return

        # Create buckets dictionary with format:
        # {
        #     "NDQ.AX+IVV.AX":
        #         {
        #             "tickers": ["IVV.AX"+"NDQ.AX"],
        #             "value": 100000,
        #             "targetPerc": 25
        #         }
        # }
        
        totalValue = 0
        buckets = {}
        for tickerGroup in self.portfolioBalance.keys():            
            buckets[tickerGroup] = {}
            tickers = tickerGroup.split('+')
            buckets[tickerGroup]["tickers"] = tickers
            buckets[tickerGroup]["targetPerc"] = self.portfolioBalance[tickerGroup]

            prices = self.getTickerPrices(tickers)
            value = 0
            for ticker, price in prices.items():
                volume = self.investments[ticker]['volume']
                value += round(volume * price, 2)

            buckets[tickerGroup]["value"] = value
            totalValue += value

        highestPercDiff = 0
        highestBucket = ""
        for bucket in buckets:
            currentPerc = (buckets[bucket]['value'] / totalValue) * 100
            buckets[bucket]['currentPerc'] = currentPerc
            targetPercDiff = (currentPerc - buckets[bucket]['targetPerc']) * (100 / buckets[bucket]['targetPerc'])
            if targetPercDiff > highestPercDiff:
                highestPercDiff = targetPercDiff
                highestBucket = bucket

        if not targetTotalValue:
            targetTotalValue = buckets[highestBucket]['value'] * (100 / buckets[highestBucket]['targetPerc'])

        dfRows = []
        for tickerGroup in buckets:
            targetValue = targetTotalValue * (buckets[tickerGroup]['targetPerc'] / 100)
            targetDiff = targetValue - buckets[tickerGroup]['value']
            dfRows.append([
                tickerGroup, 
                format(buckets[tickerGroup]['currentPerc'], '.2f'), 
                format(buckets[tickerGroup]['targetPerc'], '.2f'), 
                format(buckets[tickerGroup]['value'], '.2f'), 
                format(targetValue, '.2f'), 
                format(targetDiff, '.2f')
            ])

        outputDf = pd.DataFrame(dfRows, columns=['Ticker Group', 'Current %', 'Target %', 'Value', 'Target Value', 'Suggestion'])
        print(f'\n{outputDf.to_string(index=False)}\n')
