from kiteconnect import KiteConnect
from datetime import datetime,timedelta
import pandas as pd
import calendar
import pytz
import os

class OptionsTradingSymbols:

    def __init__(self):
        self.tz = pytz.timezone('Asia/Kolkata')

        self.api_key = '9fua69n6l7whujs5'
        self.access_token = '9yQ3GUGiQ74c8mepSreb95vXEH0YhF6L'

        self.kite = KiteConnect(api_key=self.api_key,timeout=20)
        self.kite.set_access_token(self.access_token)

        self.monthlyContractOptionFlag = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
        
        self.tradeSymbol = 'BANKNIFTY'
        self.high = 34801.95
        self.strikePrice = None
        self.tradingSymbol = None
        self.options_token = None
        self.isWeeklyOption = False

    def roundup(self,x):
        return x if x % 100 == 0 else x + 100 - x % 100

    def generateStrikePrice(self):
        roundupNum = self.roundup(int(self.high))
        if (roundupNum - int(self.high)) > 50:
            self.strikePrice = roundupNum
        else:
            self.strikePrice = roundupNum + 100
    
        print('STRIKE PRICE : {}'.format(self.strikePrice))

    def generateTradingTokens(self,current_day,fetching_month,fetching_year):
        # Fetching Months
        month = calendar.monthcalendar(fetching_year, fetching_month)
        thursdayList = []
        for i in range(len(month)):
            thursday = month[i][calendar.THURSDAY]
            if thursday != 0:
                thursdayList.append(thursday)
        
        if len(thursdayList) > 4:
            # week have 5 thursday 
            isMonthlyOptionExpired = True

            for i in range(len(thursdayList)):
                thursday = thursdayList[i]
                if thursday > current_day:
                    # so leave first and last one
                    firstThursday = thursdayList[0]
                    print('firstThursday : {}'.format(firstThursday))

                    lastThursday = thursdayList[-1]
                    print('pickedThursday : {}'.format(thursday))

                    yearLabel = str(fetching_year)
                    yearLabel = yearLabel[-2:]
                    self.tradingSymbol = self.tradeSymbol + yearLabel + self.monthlyContractOptionFlag[fetching_month-1] + 'FUT'
                    print('MAIN TRADING SYMBOL : {}'.format(self.tradingSymbol))

                    if (thursday == firstThursday) or (thursday == lastThursday):
                        # Look For Monthly Option Contract
                        self.options_token = self.tradeSymbol + yearLabel + self.monthlyContractOptionFlag[fetching_month-1]+str(self.strikePrice)+'CE'
                        self.isWeeklyOption = False
                    else:
                        # Look For Weekly Option Contract
                        # year: 2 digit , month: 1 digit except OCT,NOV,DEC , date: always 2 digit
                        self.options_token = self.tradeSymbol+ yearLabel+str(fetching_month) + str('%02d' % thursday)+str(self.strikePrice)+'CE'
                        self.isWeeklyOption = True
                        
                    if self.isWeeklyOption:
                        print('WEEKLY OPTIONS TRADING SYMBOL : {}'.format(self.options_token))
                    else:
                        print('MONTHLY OPTIONS TRADING SYMBOL : {}'.format(self.options_token))

                    isMonthlyOptionExpired = False
                    break

            if isMonthlyOptionExpired:
                print('Current month future expired ! Switching to next month')
                # Change Month
                # If Current Month Is DEC Then Change MONTH TO NEW YEAR
                if fetching_month ==12:
                    # Change Year , Change Month
                    fetchingYear = fetching_year +1
                    # In this case new month always would be JAN
                    fetchingMonth = 1
                else:
                    # keey the year same
                    fetchingYear = fetching_year
                    # change month only
                    fetchingMonth = fetching_month+1
        
                # So Fetch Again
                self.generateTradingTokens(1,fetchingMonth,fetchingYear)
        else:
            # Its a 4 week month
            isMonthlyOptionExpired = True
        
            for i in range(len(thursdayList)):
                thursday = thursdayList[i]
                if thursday > current_day :
                    lastThursday = thursdayList[-1]
                    print('pickedThursday : {}'.format(thursday))

                    yearLabel = str(fetching_year)
                    yearLabel = yearLabel[-2:]
                    self.tradingSymbol = self.tradeSymbol + yearLabel + self.monthlyContractOptionFlag[fetching_month-1] + 'FUT'
                    print('MAIN TRADING SYMBOL : {}'.format(self.tradingSymbol))

                    if (thursday == lastThursday):
                        # Look For Monthly Option Contract
                        self.options_token = self.tradeSymbol + yearLabel + self.monthlyContractOptionFlag[fetching_month-1]+str(self.strikePrice)+'CE'
                        self.isWeeklyOption = False
                    else:
                        # Look For Weekly Option Contract
                        # year: 2 digit , month: 1 digit except OCT,NOV,DEC , date: always 2 digit
                        self.options_token = self.tradeSymbol+ yearLabel+str(fetching_month) + str('%02d' % thursday)+str(self.strikePrice)+'CE'
                        self.isWeeklyOption = True

                    if self.isWeeklyOption:
                        print('WEEKLY OPTIONS TRADING SYMBOL : {}'.format(self.options_token))
                    else:
                        print('MONTHLY OPTIONS TRADING SYMBOL : {}'.format(self.options_token))

                    isMonthlyOptionExpired = False
                    break

            if isMonthlyOptionExpired:
                print('Current month future expired ! Switching to next month')
                # Change Month
                # If Current Month Is DEC Then Change MONTH TO NEW YEAR
                if fetching_month ==12:
                    # Change Year , Change Month
                    fetchingYear = fetching_year +1
                    # In this case new month always would be JAN
                    fetchingMonth = 1
                else:
                    # keep the year same
                    fetchingYear = fetching_year
                    # change month only
                    fetchingMonth = fetching_month + 1
        
                # So Fetch Again
                self.generateTradingTokens(1,fetchingMonth,fetchingYear)

        if not isMonthlyOptionExpired:
            try:
                instrumentList =self.kite.instruments(exchange="NFO")
                isOptionTokenFound = False
                isTradingTokenFound = False
                for instrument in instrumentList:
                    trading_Symbol = str(instrument['tradingsymbol'])
                    if not isOptionTokenFound and self.options_token in trading_Symbol:
                        instrument_token = instrument['instrument_token']
                        token = {}
                        token[self.options_token] = instrument_token
                        isOptionTokenFound = True
                        if self.isWeeklyOption:
                            print('WEEKLY OPTION TRADING TOKEN : {}'.format(token))
                        else:
                            print('MONTHLY OPTION TRADING TOKEN : {}'.format(token))
                        
            
                    if not isTradingTokenFound and self.tradingSymbol in trading_Symbol:
                        instrument_token = instrument['instrument_token']
                        token = {}
                        token[self.tradingSymbol] = instrument_token
                        print('MAIN TRADING TOKEN : {}'.format(token))
                        isTradingTokenFound = True
            
                    if isOptionTokenFound and isTradingTokenFound:
                        break
            
                print('--------- END FETCHING INSTRUMENT LIST ---------------')
            except Exception as e:
                print(e)

if __name__ == '__main__':
    # use month in single digi ex. JAN = 1 , FEB = 2 except OCT,NOV,DEC . OCT = 10
    # change the date and run python test.py in terminal to see out put 
    # Kite Access-Token and Api-Key added hardcoded 
    day = 28
    month = 1
    year = 2022

    # Passing Date
    print('INPUT DATE : {}-{}-{}'.format(day,month,year))

    optionTradingSymbol = OptionsTradingSymbols()
    optionTradingSymbol.generateStrikePrice()
    optionTradingSymbol.generateTradingTokens(day,month,year)

    








    



    
    
    