from kiteconnect import KiteConnect
from datetime import datetime,timedelta
import calendar
import pandas as pd
import pandas_ta as ta
import time
import json
import os
import pytz


class BankNifty:

    def __init__(self,socketio,selectedInterval):

        self.socketio = socketio

        # Api key and access token
        with open('access_token.json', 'r') as openfile:
            accessTokenObj = json.load(openfile)
            self.access_token = accessTokenObj['access_token']

        self.api_key = '9fua69n6l7whujs5'

        self.kite = KiteConnect(api_key=self.api_key,timeout=20)
        self.kite.set_access_token(self.access_token)

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
        self.tokens ={18257666 : 'BANKNIFTY21DECFUT'}
        self.options_token = None

        # find options expiry flag
        month = calendar.monthcalendar(now.year, now.month)
        today = now.day

        if len(month) > 4:
            # week have 5 thursday 
            # so leave first and last one
            firstThursday = month[0][calendar.THURSDAY]
            print('firstThursday : {}'.format(firstThursday))

            lastThursday = month[-1][calendar.THURSDAY]
            print('lastThursday : {}'.format(lastThursday))

            for i in range(len(month)):
                thursday = month[i][calendar.THURSDAY]
                if thursday > today :
                    if (thursday == firstThursday) or (thursday == lastThursday):
                        self.options_token = 'BANKNIFTY21DEC'
                    else:
                        self.options_token = 'BANKNIFTY21D{}'.format(thursday)

                    print(self.options_token)
                    break
        else:
            lastThursday = month[-1][calendar.THURSDAY]
            print('lastThursday : {}'.format(lastThursday))

            for i in range(len(month)):
                thursday = month[i][calendar.THURSDAY]
                if thursday > today :
                    if (thursday == lastThursday):
                        self.options_token = 'BANKNIFTY21DEC'
                    else:
                        self.options_token = 'BANKNIFTY21D{}'.format(thursday)
            
                    print(self.options_token)
                    break

        # Log String
        self.logMessage = 'Bank Nifty Script Started...'
        self.sendLogReport(self.logMessage)
        self.logMessage = 'Script automatically executed at an interval of ' +"' " +self.candleInterval+" '"
        self.sendLogReport(self.logMessage)
        
        self.option_instrument_token = None
        self.option_lot_size = None
        self.option_exchange = None
        self.logReport = None
        self.TERMINATE_BANK_NIFTY = None

    def stopThread(self):
        print('stop Bank Nifty Thread called....')
        self.TERMINATE_BANK_NIFTY = True

    def startBankNiftyAlgo(self,timeInterval):

        self.TERMINATE_BANK_NIFTY = False

        try:
            while not self.TERMINATE_BANK_NIFTY:

                now = datetime.now()
                now = now.astimezone(self.tz)

                if now.second == int(timeInterval) and now.minute % int(timeInterval) == 0:
                    self.currentTime ='%02d:%02d:%02d' % (now.hour,now.minute,now.second)
                    logString = 'Start Checking At : ' + str(self.currentTime)
                    self.sendLogReport(logString)

                    self.fetchedCandleTime ='%02d:%02d:%02d' % (now.hour,now.minute-int(timeInterval),now.second-int(timeInterval))
                    logString = 'Fetched Candle Time : ' + str(self.fetchedCandleTime)
                    self.sendLogReport(logString)

                    # Now Checking Bank Nifty
                    time.sleep(1)
                    self.checkBankNifty(timeInterval)
        
        except Exception as ex:
            print(ex)
            logString = str(ex)
            self.sendLogReport(logString)
            self.socketio.emit('force_stop_bank_nifty_script')

    def checkBankNifty(self,timeInterval):
        logString = 'Please wait while checking " BANK NIFTY " futures...'
        self.sendLogReport(logString)

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
                logString ='TRIGGER CANDLE FOUND : '
                self.sendLogReport(logString)
                logString ='Please wait , now looking for trade ... '
                self.sendLogReport(logString)

                # Now Check for trade
                # Rules for trade : ltp must cross triggerCandleLow
                # Means when ltp would be lower than triggerCandleLow

                NEED_TO_EXIT_TRADE_LOOP = False
                while not NEED_TO_EXIT_TRADE_LOOP:
                    now = datetime.now()
                    now = now.astimezone(self.tz)

                    if now.second == 57 and now.minute % (int(timeInterval)-1) == 0:
                        NEED_TO_EXIT_TRADE_LOOP = True

                    symbol = "NFO:{}".format(str(self.tokens[token]))
                    ltp = self.kite.ltp([symbol])
                    latestPrice = ltp[symbol]['last_price']

                    print('we are fetching ltp for trade : {}'.format(latestPrice))

                    if triggerCandleLow > latestPrice:

                        # Send log about trade executed time
                        tradeExecutedTime ='%02d:%02d:%02d' % (now.hour,now.minute,now.second)
                        logString = 'TRADE EXECUTED At : ' + str(tradeExecutedTime)
                        self.sendLogReport(logString)

                        # Now we search for best matching options
                        logString = 'Now fetching best matching options for trade '
                        self.sendLogReport(logString)

                        # Options finding strategy
                        # ---------------------------------
                        # If triggerCandleHigh is 440 then find option 500 
                        # And if triggerCandleHigh is 460 then find option 600
                        roundupNum = self.roundup(int(triggerCandleHigh))
                        if (roundupNum - int(triggerCandleHigh)) > 50:
                            strikePrice = roundupNum
                        else:
                            strikePrice = roundupNum + 100

                        logString = 'Selected STRIKE PRICE on the basis of CANDLE HIGH : ' + str(strikePrice)
                        self.sendLogReport(logString)
                        logString ='Please wait , while searching options with strike price : {}'.format(strikePrice)
                        self.sendLogReport(logString)

                        # Create option trading symbol
                        self.options_token = self.options_token + str(strikePrice) + "CE"
                        print(self.options_token)

                        # Fetching Instruments
                        instrumentList = self.kite.instruments(exchange="NFO")
                        print('instrumentList printed')
                        for instrument in instrumentList:
                            tradingSymbolOptions = str(instrument['tradingsymbol'])
                            if self.options_token == tradingSymbolOptions:
                                logString = '------------------------'
                                self.sendLogReport(logString)
                                logString = 'BEST MATCHING OPTIONS : ' + str(tradingSymbolOptions)
                                self.sendLogReport(logString)
                                expiry = instrument['expiry']
                                logString = 'EXPIRE ON : {}'.format(expiry)
                                self.sendLogReport(logString)

                                symbol = "NFO:{}".format(tradingSymbolOptions)
                                ltp = self.kite.ltp([symbol])
                                optionLatestPrice = ltp[symbol]['last_price']
                                logString = 'LAST PRICE : {}'.format(optionLatestPrice)
                                self.sendLogReport(logString)
                                logString = '------------------------'
                                self.sendLogReport(logString)

                                self.option_instrument_token = str(instrument['instrument_token'])
                                self.option_lot_size = instrument['lot_size']
                                self.option_exchange = str(instrument['exchange'])
                                break
                                    

                        now = datetime.now()
                        now = now.astimezone(self.tz)
                        till_date = self.to_date + ' ' + '%02d:%02d:%02d' % (now.hour,now.minute,now.second)
          
                        # Now Fetch candle data of fetched/selected options
                        optionsRecords = self.kite.historical_data(self.option_instrument_token, 
                                        from_date=self.from_date, 
                                        to_date=till_date, 
                                        interval=self.candleInterval)

                        # Bank Nifty Options Data Frame
                        bankNiftyOptionsDF = pd.DataFrame(optionsRecords)
                        bankNiftyOptionsDF.drop(bankNiftyOptionsDF.tail(1).index,inplace=True)

                        # Fetching latest Candle
                        latestCandle = bankNiftyOptionsDF.iloc[-1]

                        optionHigh = latestCandle['high']
                        optionLow = latestCandle['low']
                        optionOpen = latestCandle['open']
                        optionClose = latestCandle['close']

                        # Execute Option Sell Order

                        # Exit Checking
                        NEED_TO_EXIT_TRADE_LOOP = True
                        isTraded = True

            if not isTraded:
                logString = '----------------------------------'
                self.sendLogReport(logString)
                logString ='TRADINGSYMBOL : ' + str(self.tokens[token])
                self.sendLogReport(logString)
                logString ='OPEN PRICE : ' + str(round(triggerCandleOpen,2))
                self.sendLogReport(logString)
                logString ='CLOSE PRICE : ' + str(round(triggerCandleClose,2))
                self.sendLogReport(logString)
                logString ='CANDLE LOW : ' + str(round(triggerCandleLow,2))
                self.sendLogReport(logString)
                logString = "EMA 5 : " + str(round(triggerCandleEMA5,2))
                self.sendLogReport(logString)
                logString = '----------------------------------'
                self.sendLogReport(logString)
            else:
                # Place Sell Order
                order_id = self.kite.place_order(variety=self.kite.VARIETY_REGULAR,
                                                exchange =self.option_exchange,
                                                tradingsymbol =tradingSymbolOptions,
                                                transaction_type = self.kite.TRANSACTION_TYPE_SELL,
                                                quantity = self.option_lot_size,
                                                product = 'MIS',
                                                order_type = 'MARKET',
                                                tag='XCS')

                logString = '***************************'
                self.sendLogReport(logString)
                logString ='TRADINGSYMBOL : ' + str(tradingSymbolOptions)
                self.sendLogReport(logString)
                logString ='***************************'
                self.sendLogReport(logString)
                logString ='# SELL SIGNAL #'
                self.sendLogReport(logString)
                logString ='ORDER ID : ' + str(order_id)
                self.sendLogReport(logString)
                logString ='OPEN PRICE : ' + str(round(optionOpen,2))
                self.sendLogReport(logString)
                logString ='CLOSE PRICE : ' + str(round(optionClose,2))
                self.sendLogReport(logString)
                logString = 'Executed Order On Price : ' + str(round(optionLatestPrice,2))
                logString ='STOP LOSS : ' + str(round(optionHigh,2))
                self.sendLogReport(logString)

                targetPrice =optionLatestPrice - ((optionHigh - optionLatestPrice) * 2) 
                logString = 'TARGET PRICE : ' + str(round(targetPrice,2))
                self.sendLogReport(logString)

                logString = '------------------------'
                self.sendLogReport(logString)

                # Now update json file 
                with open("bank_nifty_script_running_status.json", "r") as jsonFile:
                    script_running_staus = json.load(jsonFile)

                # Update Script Running Status
                script_running_staus["is_trade_executed"] = True
                with open("bank_nifty_script_running_status.json", "w") as jsonFile:
                    json.dump(script_running_staus, jsonFile)

                
                # Look for exit position
                logString = 'Now look for exit position'
                self.sendLogReport(logString)
                logString = 'Either StopLoss or Target acheived we exit the position'
                self.sendLogReport(logString)
                logString = '------------------------'
                self.sendLogReport(logString)
                logString = 'STOP_LOSS : {}'.format(str(round(optionHigh,2))) +'  ' +'TARGET : {}'.format(str(round(targetPrice,2)))
                self.sendLogReport(logString)
                logString = '------------------------'
                self.sendLogReport(logString)
                logString = 'Please wait for stoploss or target to hit...'
                self.sendLogReport(logString)

                while script_running_staus["is_trade_executed"] :

                    symbol = "NFO:{}".format(str(tradingSymbolOptions))
                    ltp = self.kite.ltp([symbol])
                    latestPrice = ltp[symbol]['last_price']

                    if latestPrice >=optionHigh:
                        # Stop Loss Hit
                        # Place Buy Order
                        order_id = self.kite.place_order(variety=self.kite.VARIETY_REGULAR,
                                                exchange =self.option_exchange,
                                                tradingsymbol =tradingSymbolOptions,
                                                transaction_type = self.kite.TRANSACTION_TYPE_BUY,
                                                quantity = self.option_lot_size,
                                                product = 'MIS',
                                                order_type = 'MARKET',
                                                tag='XCS')

                        logString ='***************************'
                        self.sendLogReport(logString)
                        logString = 'STOP LOSS HIT : {}'.format(tradingSymbolOptions)
                        self.sendLogReport(logString)
                        tradeExecutedTime ='%02d:%02d:%02d' % (now.hour,now.minute,now.second)
                        logString = 'STOP LOSS HIT At : ' + str(tradeExecutedTime)
                        self.sendLogReport(logString)
                        logString = '# EXECUTE BUY ORDER #'
                        self.sendLogReport(logString)
                        logString = 'ORDER ID : {}'.format(order_id)
                        self.sendLogReport(logString)
                        logString = 'LATEST PRICE : {}'.format(latestPrice)
                        self.sendLogReport(logString)

                        # Update Script Running Status
                        script_running_staus["is_trade_executed"] = False
                        with open("bank_nifty_script_running_status.json", "w") as jsonFile:
                            json.dump(script_running_staus, jsonFile)

                    elif latestPrice <= targetPrice :
                        # Target Hit
                        # Place Buy Order
                        order_id = self.kite.place_order(variety=self.kite.VARIETY_REGULAR,
                                                exchange =self.option_exchange,
                                                tradingsymbol =tradingSymbolOptions,
                                                transaction_type = self.kite.TRANSACTION_TYPE_BUY,
                                                quantity = self.option_lot_size,
                                                product = 'MIS',
                                                order_type = 'MARKET',
                                                tag='XCS')

                        logString ='***************************'
                        self.sendLogReport(logString)
                        logString = 'TARGET HIT : {}'.format(tradingSymbolOptions)
                        self.sendLogReport(logString)
                        tradeExecutedTime ='%02d:%02d:%02d' % (now.hour,now.minute,now.second)
                        logString = 'TARGET HIT At : ' + str(tradeExecutedTime)
                        self.sendLogReport(logString)
                        logString = '# EXECUTE BUY ORDER #'
                        self.sendLogReport(logString)
                        logString = 'ORDER ID : {}'.format(order_id)
                        self.sendLogReport(logString)
                        logString = 'LATEST PRICE : {}'.format(latestPrice)
                        self.sendLogReport(logString)

                        # Update Script Running Status
                        script_running_staus["is_trade_executed"] = False
                        with open("bank_nifty_script_running_status.json", "w") as jsonFile:
                            json.dump(script_running_staus, jsonFile)

                    time.sleep(0.5)

        if not isTraded:
            logString = 'No trade this session...'
            self.sendLogReport(logString)
            logString = '--------End-----------'
            self.sendLogReport(logString)
        else:
            logString = '--------End-----------'
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