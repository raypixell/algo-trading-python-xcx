from kiteconnect import KiteConnect
from datetime import datetime,timedelta,time
import calendar
import pandas as pd
import pandas_ta as ta
import time as tm
import requests
import json
import os
import pytz


class BankNifty:

    def __init__(self,socketio,selectedInterval):

        self.socketio = socketio

        self.api_key = '9fua69n6l7whujs5'
        self.access_token = None

        self.REPORT_FILE_NAME = 'bank_nifty_stats_report.xlsx'

        self.tz = pytz.timezone('Asia/Kolkata')
        self.currentTime = None

        # Log file name
        now = datetime.now()
        now = now.astimezone(self.tz)
        
        self.DOWNLOAD_LOG_FILE_NAME = "bank_nifty_" + '%02d-%02d-%02d.txt' % (now.day,now.month,now.year)
        print(self.DOWNLOAD_LOG_FILE_NAME)

        self.candleInterval = selectedInterval
        self.no_of_days_for_candle_data = 1
        self.quantity = 1

        self.from_date = datetime.strftime(now - timedelta(self.no_of_days_for_candle_data),"%Y-%m-%d")
        self.to_date = datetime.today().strftime('%Y-%m-%d')

        # bank nifty instrument token
        self.tokens = None
        self.logReport = None
        self.TERMINATE_BANK_NIFTY = False
        self.IS_ITS_MARKET_TIME = True

        # trading symbol constants
        self.monthlyContractOptionFlag = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
        self.tradeSymbol = 'BANKNIFTY'
        self.tradingSymbol = None
        self.options_token = None
        self.option_instrument_token = None
        self.option_lot_size = None
        self.option_exchange = None
        self.isWeeklyOption = False   
        self.fetchedCandleTime = None

        self.dashedLabel = '---------------------------------------------------------------------------------------------------'
        self.spaceGap = 20

    def doLogin(self):
        self.kite = KiteConnect(api_key=self.api_key,timeout=20)
        self.kite.set_access_token(self.access_token)

    def fetchAccessToken(self):
        # Fetch Access-Token From Api
        accessTokenUrl = 'https://www.zigtap.com/zerodha/myaccesstoken.txt'
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
            uResponse = requests.get(accessTokenUrl , headers=headers)
            self.access_token = uResponse.text
        except requests.ConnectionError as ex:
            print(ex)
            logString = str(ex)
            self.sendLogReport(logString)
            self.TERMINATE_BANK_NIFTY = True
            self.socketio.emit('force_stop_bank_nifty_script')
        
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
                        self.options_token = self.tradeSymbol + yearLabel + self.monthlyContractOptionFlag[fetching_month-1]
                        self.isWeeklyOption = False
                    else:
                        # Look For Weekly Option Contract
                        # year: 2 digit , month: 1 digit except OCT,NOV,DEC , date: always 2 digit
                        self.options_token = self.tradeSymbol+ yearLabel+str(fetching_month) + str('%02d' % thursday)
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
                if thursday >= current_day :
                    lastThursday = thursdayList[-1]
                    print('pickedThursday : {}'.format(thursday))

                    yearLabel = str(fetching_year)
                    yearLabel = yearLabel[-2:]
                    self.tradingSymbol = self.tradeSymbol + yearLabel + self.monthlyContractOptionFlag[fetching_month-1] + 'FUT'
                    print('MAIN TRADING SYMBOL : {}'.format(self.tradingSymbol))

                    if (thursday == lastThursday):
                        # Look For Monthly Option Contract
                        self.options_token = self.tradeSymbol + yearLabel + self.monthlyContractOptionFlag[fetching_month-1]
                        self.isWeeklyOption = False
                    else:
                        # Look For Weekly Option Contract
                        # year: 2 digit , month: 1 digit except OCT,NOV,DEC , date: always 2 digit
                        self.options_token = self.tradeSymbol+ yearLabel+str(fetching_month) + str('%02d' % thursday)
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
            

    def stopThread(self):
        print('stop Bank Nifty Thread called....')
        self.TERMINATE_BANK_NIFTY = True

    def isNowInTimePeriod(self,startTime, endTime, nowTime):
        if startTime < endTime:
            return nowTime >= startTime and nowTime <= endTime
        else:
            return nowTime >= startTime or nowTime <= endTime

    def checkWeekDay(self):
        now = datetime.now()
        now = now.astimezone(self.tz)
        today = now.day

        month = calendar.monthcalendar(now.year, now.month)

        for week in month:
            if today in week:
                saturday = week[calendar.SATURDAY]
                sunday = week[calendar.SUNDAY]

                if today == saturday or today == sunday:
                    # Its a weekend
                    logString = 'MARKET CLOSED ON WEEK DAYS'
                    self.sendLogReport(logString)
                    self.TERMINATE_BANK_NIFTY = True
                    self.socketio.emit('force_stop_bank_nifty_script')
                else:
                    if not self.isNowInTimePeriod(time(9,15), time(15,30), now.time()):
                        logString = 'MARKET CLOSED'
                        self.sendLogReport(logString)
                        self.TERMINATE_BANK_NIFTY = True
                        self.socketio.emit('force_stop_bank_nifty_script')
                    

    def startBankNiftyAlgo(self,timeInterval):
        
        try:
            # First check its not a week day
            self.checkWeekDay()

            if not self.TERMINATE_BANK_NIFTY:
                # Now fetch access-token from api
                self.fetchAccessToken()
                self.doLogin()

                # push login message to client
                logString = self.dashedLabel
                self.sendLogReport(logString)
                logString = 'LOGGED IN SUCCESSFULLY'
                self.sendLogReport(logString)
                logString = self.dashedLabel
                self.sendLogReport(logString)
                
                # Now generate trading token
                now = datetime.now()
                now = now.astimezone(self.tz)
                self.generateTradingTokens(now.day,now.month,now.year)

                instrumentList =self.kite.instruments(exchange="NFO")
                for instrument in instrumentList:
                    trading_Symbol = str(instrument['tradingsymbol'])
                    
                    if self.tradingSymbol in trading_Symbol:
                        instrument_token = instrument['instrument_token']
                        self.tokens = {}
                        self.tokens[instrument_token] = self.tradingSymbol
                        print('MAIN TRADING TOKEN : {}'.format(self.tokens))
                        break
            
                print('--------- END FETCHING INSTRUMENT LIST ---------------')

                # Print log message about script started
                # Log String
                
                logString = 'SYMBOL : {}'.format(self.tradingSymbol)
                self.sendLogReport(logString)

                newDate = datetime.strftime(now,'%d %b, %Y - %I : %M %p')
                logString = 'Algo Start Date / Time : {}'.format(newDate)
                self.sendLogReport(logString)

                logString = self.dashedLabel
                self.sendLogReport(logString)

                timeLabel = "Time"
                lowLabel = "Low"
                emaLabel = "Ema"
                tradeLabel = "Trade"

                logString = timeLabel.center(self.spaceGap) + "|" + lowLabel.center(self.spaceGap) + "|" + emaLabel.center(self.spaceGap) + "|" + tradeLabel.center(self.spaceGap)
                self.sendLogReport(logString)
                logString = self.dashedLabel
                self.sendLogReport(logString)

                while not self.TERMINATE_BANK_NIFTY:
                    now = datetime.now()
                    now = now.astimezone(self.tz)

                    if not self.isNowInTimePeriod(time(9,15), time(15,30), now.time()):
                        logString = 'MARKET CLOSED'
                        self.sendLogReport(logString)
                        self.TERMINATE_BANK_NIFTY = True
                        self.socketio.emit('force_stop_bank_nifty_script')
                    else:
                        if now.second == int(timeInterval) and now.minute % int(timeInterval) == 0:
                            executedCandleTime = now - timedelta(minutes=5)
                            self.fetchedCandleTime ='%02d:%02d' % (executedCandleTime.hour,executedCandleTime.minute)

                            # Now Checking Bank Nifty
                            tm.sleep(1)
                            self.checkBankNifty(timeInterval)
        
        except Exception as ex:
            print(ex)
            logString = str(ex)
            self.sendLogReport(logString)
            self.TERMINATE_BANK_NIFTY = True
            self.socketio.emit('force_stop_bank_nifty_script')       

    def checkBankNifty(self,timeInterval):

        isTraded = False
        for token in self.tokens:
            now = datetime.now()
            now = now.astimezone(self.tz)
            till_date = self.to_date + ' ' + '%02d:%02d:%02d' % (now.hour,now.minute,5)
            records = self.kite.historical_data(token, 
                    from_date=self.from_date, 
                    to_date=till_date, 
                    interval=self.candleInterval)

            # Bank Nifty Data Frame
            bankNiftyDF = pd.DataFrame(records)
            bankNiftyDF.drop(bankNiftyDF.tail(1).index,inplace=True)

            # Calculating EMA5
            bankNiftyDF["ema5"] = ta.ema(bankNiftyDF['close'], length=5)

            # Convert date type to excel supported date type
            bankNiftyDF['date'] = bankNiftyDF['date'].apply(lambda a: pd.to_datetime(a).date())
            bankNiftyDF.to_excel(self.REPORT_FILE_NAME)

            # Fetching Trigger Candle in latest Candle
            triggerCandle = bankNiftyDF.iloc[-1]

            triggerCandleClose = triggerCandle['close']
            triggerCandleOpen = triggerCandle['open']
            triggerCandleHigh = triggerCandle['high']
            triggerCandleLow = triggerCandle['low']
            triggerCandleEMA5 = triggerCandle['ema5']

            # Script is made for only sell futures
            # So checking sell condition
            # Rule 1 : trigger candle low must be above ema5
            # Rule 2 : current candle must cross trigger candle low

            if triggerCandleLow > triggerCandleEMA5:

                # Trigger candle found
                # Now fetch Options 
                # Strike price would be triggerd candle high
                # ---------------------------------
                # Options finding strategy
                # If triggerCandleHigh is 440 then find option 500 
                # And if triggerCandleHigh is 460 then find option 600

                roundupNum = self.roundup(int(triggerCandleHigh))
                if (roundupNum - int(triggerCandleHigh)) > 50:
                    strikePrice = roundupNum
                else:
                    strikePrice = roundupNum + 100

                # Create option trading symbol
                self.options_token = self.options_token + str(strikePrice) + "CE"
                print(self.options_token)

                # Fetching instrument id of selected option
                instrumentList = self.kite.instruments(exchange="NFO")
                for instrument in instrumentList:
                    tradingSymbolOptions = str(instrument['tradingsymbol'])
                    if self.options_token == tradingSymbolOptions:        
                        self.option_instrument_token = str(instrument['instrument_token'])
                        self.option_lot_size = instrument['lot_size']
                        self.option_exchange = str(instrument['exchange'])
                        break

                # Now fetch selected Options data
                now = datetime.now()
                now = now.astimezone(self.tz)
                till_date = self.to_date + ' ' + '%02d:%02d:%02d' % (now.hour,now.minute,now.second)
          
                # Now Fetch candle data of fetched/selected options
                optionsRecords = self.kite.historical_data(self.option_instrument_token, 
                                from_date=self.from_date, 
                                to_date=till_date, 
                                nterval=self.candleInterval)

                # Bank Nifty Options Data Frame
                bankNiftyOptionsDF = pd.DataFrame(optionsRecords)
                bankNiftyOptionsDF.drop(bankNiftyOptionsDF.tail(1).index,inplace=True)

                # Fetching latest Candle
                latestCandle = bankNiftyOptionsDF.iloc[-1]

                optionHigh = latestCandle['high']
                optionLow = latestCandle['low']
                optionOpen = latestCandle['open']
                optionClose = latestCandle['close']

                # Now we have spent some time in finding options data
                # We only need to check for trade within current 5 min timeInterval
                # So go 5 minutes into the future
                later5min = now + timedelta(0,0,0,0,int(timeInterval))
                # Then round to current 5 minutes
                EXECUTED_TILL = datetime(later5min.year, later5min.month, later5min.day, later5min.hour, int(timeInterval)*int(later5min.minute/int(timeInterval)), 0, 0)
                print("Now loop will contineu for next  : ", EXECUTED_TILL.hour , ":" , EXECUTED_TILL.minute)

                # Now Check for trade
                # Rules for trade : options ltp must cross optionsCandleLow
                # Means when options ltp would be lower than optionsCandleLow

                NEED_TO_EXIT_TRADE_LOOP = False
                while not NEED_TO_EXIT_TRADE_LOOP:
                    now = datetime.now()
                    now = now.astimezone(self.tz)

                    if now.minute == EXECUTED_TILL.minute:
                        NEED_TO_EXIT_TRADE_LOOP = True
                    else:
                        symbol = "NFO:{}".format(self.options_token)
                        ltp = self.kite.ltp([symbol])
                        latestPrice = ltp[symbol]['last_price']

                        if optionLow > latestPrice:
                            # Trade executed
                            NEED_TO_EXIT_TRADE_LOOP = True
                            isTraded = True

            if not isTraded:
                lowLabel = str(round(triggerCandleLow,2))
                emaLabel = str(round(triggerCandleEMA5,2))
                
                logString = self.fetchedCandleTime.center(self.spaceGap) + "|" + lowLabel.center(self.spaceGap) + "|" + emaLabel.center(self.spaceGap) + "|" + str(isTraded).center(self.spaceGap)
                self.sendLogReport(logString)
                logString = self.dashedLabel
                self.sendLogReport(logString)
            else:
                # Place Sell Order
                order_id = self.kite.place_order(variety=self.kite.VARIETY_REGULAR,
                                exchange =self.option_exchange,
                                tradingsymbol =self.options_token,
                                transaction_type = self.kite.TRANSACTION_TYPE_SELL,
                                quantity = self.option_lot_size,
                                product = 'MIS',
                                order_type = 'MARKET',
                                tag='XCS')

                # Send log about trade executed time
                now = datetime.now()
                now = now.astimezone(self.tz)
                tradeExecutedTime ='%02d:%02d' % (now.hour,now.minute)

                lowLabel = str(round(triggerCandleLow,2))
                emaLabel = str(round(triggerCandleEMA5,2))
                
                logString = tradeExecutedTime.center(self.spaceGap) + "|" + lowLabel.center(self.spaceGap) + "|" + emaLabel.center(self.spaceGap) + "|" + str(isTraded).center(self.spaceGap)
                self.sendLogReport(logString)
                logString = self.dashedLabel
                self.sendLogReport(logString)

                timeLabel = "Time"
                stoplossLabel = "Stoplosshit"
                targetLabel = "Targethit"
                orderLabel = "Orderid"

                logString = timeLabel.center(self.spaceGap) + "|" + stoplossLabel.center(self.spaceGap) + "|" + targetLabel.center(self.spaceGap) + "|" + orderLabel.center(self.spaceGap)
                self.sendLogReport(logString)
                logString = self.dashedLabel
                self.sendLogReport(logString)

                # Now find out target and stop loss
                stopLossPrice = int(optionHigh)
                targetPrice = (int(optionHigh) - int(optionLow))*2
                stopLoss = int(optionHigh) - int(optionLow)
                target = stopLoss*2 

                # Now update json file 
                with open("bank_nifty_script_running_status.json", "r") as jsonFile:
                    script_running_staus = json.load(jsonFile)

                # Update Script Running Status
                script_running_staus["is_trade_executed"] = True
                with open("bank_nifty_script_running_status.json", "w") as jsonFile:
                    json.dump(script_running_staus, jsonFile)

                
                # Look for exit position
                while script_running_staus["is_trade_executed"] :

                    symbol = "NFO:{}".format(self.options_token)
                    ltp = self.kite.ltp([symbol])
                    latestPrice = ltp[symbol]['last_price']

                    if latestPrice >=optionHigh:
                        # Stop Loss Hit
                        # Place Buy Order
                        order_id = self.kite.place_order(variety=self.kite.VARIETY_REGULAR,
                                        exchange =self.option_exchange,
                                        tradingsymbol =self.options_token,
                                        transaction_type = self.kite.TRANSACTION_TYPE_BUY,
                                        quantity = self.option_lot_size,
                                        product = 'MIS',
                                        order_type = 'MARKET',
                                        tag='XCS')

                    
                        # Update Script Running Status
                        script_running_staus["is_trade_executed"] = False
                        with open("bank_nifty_script_running_status.json", "w") as jsonFile:
                            json.dump(script_running_staus, jsonFile)

                        # Send log report to client
                        now = datetime.now()
                        now = now.astimezone(self.tz)
                        tradeExecutedTime ='%02d:%02d' % (now.hour,now.minute)

                        stoplossLabel = str(True)
                        targetLabel = str(False)
                
                        logString = tradeExecutedTime.center(self.spaceGap) + "|" + stoplossLabel.center(self.spaceGap) + "|" + targetLabel.center(self.spaceGap) + "|" + str(order_id).center(self.spaceGap)
                        self.sendLogReport(logString)
                        logString = self.dashedLabel
                        self.sendLogReport(logString)

                        timeLabel = "Time"
                        lowLabel = "Low"
                        emaLabel = "Ema"
                        tradeLabel = "Trade"

                        logString = timeLabel.center(self.spaceGap) + "|" + lowLabel.center(self.spaceGap) + "|" + emaLabel.center(self.spaceGap) + "|" + tradeLabel.center(self.spaceGap)
                        self.sendLogReport(logString)
                        logString = self.dashedLabel
                        self.sendLogReport(logString)

                    elif latestPrice <= targetPrice :
                        # Target Hit
                        # Place Buy Order
                        order_id = self.kite.place_order(variety=self.kite.VARIETY_REGULAR,
                                        exchange =self.option_exchange,
                                        tradingsymbol =self.options_token,
                                        transaction_type = self.kite.TRANSACTION_TYPE_BUY,
                                        quantity = self.option_lot_size,
                                        product = 'MIS',
                                        order_type = 'MARKET',
                                        tag='XCS')

                        # Update Script Running Status
                        script_running_staus["is_trade_executed"] = False
                        with open("bank_nifty_script_running_status.json", "w") as jsonFile:
                            json.dump(script_running_staus, jsonFile)

                        # Send log report to client
                        now = datetime.now()
                        now = now.astimezone(self.tz)
                        tradeExecutedTime ='%02d:%02d' % (now.hour,now.minute)

                        stoplossLabel = str(True)
                        targetLabel = str(False)
                
                        logString = tradeExecutedTime.center(self.spaceGap) + "|" + stoplossLabel.center(self.spaceGap) + "|" + targetLabel.center(self.spaceGap) + "|" + str(order_id).center(self.spaceGap)
                        self.sendLogReport(logString)
                        logString = self.dashedLabel
                        self.sendLogReport(logString)

                        timeLabel = "Time"
                        lowLabel = "Low"
                        emaLabel = "Ema"
                        tradeLabel = "Trade"

                        logString = timeLabel.center(self.spaceGap) + "|" + lowLabel.center(self.spaceGap) + "|" + emaLabel.center(self.spaceGap) + "|" + tradeLabel.center(self.spaceGap)
                        self.sendLogReport(logString)
                        logString = self.dashedLabel
                        self.sendLogReport(logString)


    def sendLogReport(self,logString):
        # write logReport to txt file
        f=open(self.DOWNLOAD_LOG_FILE_NAME, "a+")
        filesize = os.path.getsize(self.DOWNLOAD_LOG_FILE_NAME)
        if filesize == 0:
            f.write(logString)
        else:
            f.write('\n'+logString)
        
        # close file stream
        f.close()

        logData = {"logReport" : logString}

        print(logString)
        self.socketio.emit('log_report_bank_nifty',logData)

    def roundup(self,x):
        return x if x % 100 == 0 else x + 100 - x % 100
