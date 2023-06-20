import os
import json
import requests
import pandas as pd
import yfinance as yf

INVESTMENT_FILE_NAME = 'store/investments.json'
HISTORY_FILE_NAME = 'store/investment_history.json'
DIVIDEND_FILE = '/store/dividend_history.json'

# History File: tradeId:int, ticker:str, price:float, volume:int, brokerage:float, date:str
# Investment file: ticker, volume, cost, totalBrokerage, dividend
# Dividend file: ticker, date, value


class Investments:
    def __init__(self):
        self.investments = self.getInvestments()
        self.history = self.getHistory()
        self.maxId = self.getMaxId()
        self.dividends = self.getDividends()
    
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

    def getMaxId(self):
        """
        Gets largest trade ID
        """
        if len(self.history.keys()) > 0:
            return max([int(tradeId) for tradeId in self.history])
        else:
            return 0
    
    def getTickerData(self, tickers:str):
        """
        Get data for tickers from Yahoo Finance API
        """
        # TODO: Fix dividends

        tickerData = yf.Tickers(tickers)
        data = {}
        for ticker in tickers.split():
            # print(tickerData.tickers[ticker].info)
            data[ticker] = {}
            data[ticker]['price'] = tickerData.tickers[ticker].info['ask']
            data[ticker]['fullName'] = tickerData.tickers[ticker].info['longName']
            data[ticker]['yield'] = tickerData.tickers[ticker].info.get('yield', 0)
            data[ticker]['quoteType'] = tickerData.tickers[ticker].info['quoteType']
            data[ticker]['ytdReturn'] = tickerData.tickers[ticker].info.get('ytdReturn', 0)
            data[ticker]['threeYrReturn'] = tickerData.tickers[ticker].info.get('threeYearAverageReturn', 0)
            data[ticker]['fiveYrReturn'] = tickerData.tickers[ticker].info.get('fiveYearAverageReturn', 0)

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
            json.dump(self.dividends, f)
            f.close()

    def outputTickerHeader(self):
        print(f"\nTicker    {'Full Name'.ljust(60, ' ')}  Price    Cost      Value     %Gain    %NetGain  Gain      Net Gain  Dividends")


    def outputTickerValue(self, data:object, ticker:str):
        price = data[ticker]['price']
        fullName = data[ticker]['fullName']
        volume = self.investments[ticker]['volume']
        cost = self.investments[ticker]['cost']
        totalBrokerage = self.investments[ticker]['totalBrokerage']
        dividend = self.investments[ticker]['dividend']
        value = price * volume
        percGain = (value / (cost - totalBrokerage) - 1) * 100
        netPercGain = (value / cost - 1) * 100
        gain = value - (cost - totalBrokerage)
        netGain = value - cost

        print(f"{ticker.ljust(8, ' ')}  {fullName.ljust(60, ' ')}  {str(round(price, 2)).ljust(7, ' ')}  {str(round(cost, 2)).ljust(8, ' ')}  {str(round(value, 2)).ljust(8, ' ')}  {(str(round(percGain, 2)) + '%').ljust(7, ' ')}  {(str(round(netPercGain, 2)) + '%').ljust(7, ' ')}   {str(round(gain, 2)).ljust(8, ' ')}  {str(round(netGain, 2)).ljust(8, ' ')}  {str(round(dividend, 2)).ljust(7, ' ')}")

        return {'cost': cost, 'value': value, 'dividend': dividend, 'gain': gain, 'net_gain': netGain, 'brokerage': totalBrokerage}

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

        tickers = ""
        for ticker in self.investments.keys():
            tickers += f"{ticker} "
    
        data = self.getTickerData(tickers.strip())

        self.outputTickerHeader()

        totalCost = 0
        totalValue = 0
        totalDividend = 0
        totalGain = 0
        totalNetGain = 0
        totalBrokerage = 0

        tickers = [k for k, _ in sorted(self.investments.items(), key=lambda x:x[1]['cost'], reverse=True)]
        for ticker in tickers:
        # for ticker in self.investments.keys():
            values = self.outputTickerValue(data, ticker)
            totalCost += values['cost']
            totalValue += values['value']
            totalDividend += values['dividend']
            totalGain += values['gain']
            totalNetGain += values['net_gain']
            totalBrokerage += values['brokerage']
        
        percGain = (totalValue / (totalCost - totalBrokerage) - 1) * 100
        netPercGain = (totalValue / totalCost - 1) * 100
        print(f"          {'Total'.ljust(69, ' ')}  {str(round(totalCost, 2)).ljust(8, ' ')}  {str(round(totalValue, 2)).ljust(8, ' ')}  {(str(round(percGain, 2)) + '%').ljust(7, ' ')}  {(str(round(netPercGain, 2)) + '%').ljust(7, ' ')}   {str(round(totalGain, 2)).ljust(8, ' ')}  {str(round(totalNetGain, 2)).ljust(8, ' ')}  {str(round(totalDividend, 2)).ljust(7, ' ')}")
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
        Output investments to command line sorted by date
        """
        # TODO:
        
        return


    def addDividend(self, date, ticker, value):
        """
        Add dividend received
        """
        # TODO:
        
        return
    

    def estimateDividends(self):
        """
        Estimated yearly dividends
        """
        tickers = ""
        for ticker in self.investments.keys():
            tickers += f"{ticker} "
        data = self.getTickerData(tickers.strip())
        
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

