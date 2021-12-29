from kiteconnect import KiteConnect
from datetime import datetime,timedelta
import pandas as pd
import pandas_ta as ta
from tapy import Indicators
import time
import json
import os
import pytz

class GoldCommodities:

    access_token = None
    api_key = None

    LOG_FILE_NAME = None
    REPORT_FILE_NAME = None
    SCRIPT_COMMENT = None
    commoditiesLogList = None

    candleInterval = None
    no_of_days_for_candle_data = None
    quantity = None

    from_date = None
    to_date = None

    tokens = None

    logMessage = None
    logReport = None

    socketio = None
    kite = None

    DOWNLOAD_LOG_FILE_NAME = None
    tz = pytz.timezone('Asia/Kolkata')
    currentTime = None

    TERMINATE_GOLD = None

    def __init__(self,socketio,selectedInterval):

        self.socketio = socketio
        self.TERMINATE_GOLD = False

        # Api key and access token
        with open('access_token.json', 'r') as openfile:
            accessTokenObj = json.load(openfile)
            self.access_token = accessTokenObj['access_token']

        self.api_key='9fua69n6l7whujs5'

        # Log file name
        now = datetime.now()
        now = now.astimezone(self.tz)
        self.DOWNLOAD_LOG_FILE_NAME = "gold_" + '%02d-%02d-%02d.txt' % (now.day,now.month,now.year)
        print(self.DOWNLOAD_LOG_FILE_NAME)

        # Log file name
        self.LOG_FILE_NAME = 'commodities_log_gold.xlsx'
        self.REPORT_FILE_NAME = 'commodities_gold.xlsx'
        self.SCRIPT_COMMENT = 'Please wait while checking " GOLD " commodities...'
        self.commoditiesLogList = []

        # Candle duration or interval
        self.candleInterval = selectedInterval
        self.no_of_days_for_candle_data = 30
        self.quantity = 1

        # Define Range to date
        # By Default it is hard coded set for 60 days
        now = datetime.now()
        now = now.astimezone(self.tz)
        self.from_date = datetime.strftime(now - timedelta(self.no_of_days_for_candle_data),"%Y-%m-%d")
        self.to_date = datetime.today().strftime('%Y-%m-%d')

        # commodities instrument token
        self.tokens ={59844359 : 'GOLDM22JANFUT'}

    def getAccessToken(self):
        return self.access_token

    def loginKite(self):
        self.kite = KiteConnect(api_key=self.api_key,timeout=20)
        self.kite.set_access_token(self.access_token)
        
        self.logMessage = 'Gold Commodities Script Started...'
        self.sendLogReport(self.logMessage)
        self.logMessage = 'Script automatically executed at an interval of ' +"' " +self.candleInterval+" '"
        self.sendLogReport(self.logMessage)

    def stopThread(self):
        print('stopThread called....')
        self.TERMINATE_GOLD = True

    def startCommoditiesAlgo(self,timeInterval):

        self.TERMINATE_GOLD = False

        try:
            while not self.TERMINATE_GOLD:

                now = datetime.now()
                now = now.astimezone(self.tz)

                if timeInterval == 1:
                    if now.second == 5:
                        self.currentTime ='%02d-%02d-%02d  %02d:%02d' % (now.day,now.month,now.year,now.hour,now.minute)
                        logString = 'start checking at : ' + str(self.currentTime)
                        self.sendLogReport(logString)

                        # Now Checking Commodities
                        time.sleep(1)
                        self.checkComodities(timeInterval)
                    
                elif timeInterval == 5:
                    if now.second == 5 and now.minute % int(timeInterval) == 0:
                        self.currentTime ='%02d-%02d-%02d  %02d:%02d' % (now.day,now.month,now.year,now.hour,now.minute)
                        logString = 'start checking at : ' + str(self.currentTime)
                        self.sendLogReport(logString)

                        # Now Checking Commodities
                        time.sleep(1)
                        self.checkComodities(timeInterval)
                
                elif timeInterval == 10:
                    if now.second == 5 and now.minute % int(timeInterval) == 0:
                        self.currentTime ='%02d-%02d-%02d  %02d:%02d' % (now.day,now.month,now.year,now.hour,now.minute)
                        logString = 'start checking at : ' + str(self.currentTime)
                        self.sendLogReport(logString)

                        # Now Checking Commodities
                        time.sleep(1)
                        self.checkComodities(timeInterval)
                
                elif timeInterval == 15:
                    if now.second == 5 and now.minute % int(timeInterval) == 0:
                        self.currentTime ='%02d-%02d-%02d  %02d:%02d' % (now.day,now.month,now.year,now.hour,now.minute)
                        logString = 'start checking at : ' + str(self.currentTime)
                        self.sendLogReport(logString)

                        # Now Checking Commodities
                        time.sleep(1)
                        self.checkComodities(timeInterval)
                
                elif timeInterval == 30:
                    if now.second == 5 and now.minute % int(timeInterval) == 0:
                        self.currentTime ='%02d-%02d-%02d  %02d:%02d' % (now.day,now.month,now.year,now.hour,now.minute)
                        logString = 'start checking at : ' + str(self.currentTime)
                        self.sendLogReport(logString)

                        # Now Checking Commodities
                        time.sleep(1)
                        self.checkComodities(timeInterval)
                          
        except Exception as ex:
            logString = str(ex)
            self.sendLogReport(logString)
            self.socketio.emit('force_stop_script',1)
                

    def checkComodities(self,timeInterval):
        try:
            commoditiesLogDF = pd.read_excel(self.LOG_FILE_NAME)
        except Exception as ex:
            print(ex)
            commoditiesLogDF = pd.DataFrame()
            commoditiesLogDF.to_excel(self.LOG_FILE_NAME)
    
        logString = self.SCRIPT_COMMENT
        self.sendLogReport(logString)

        isTraded = False
        for token in self.tokens:
            records = self.kite.historical_data(token, 
                    from_date=self.from_date, 
                    to_date=self.to_date, 
                    interval=self.candleInterval)

            # Commodities Data Frame
            commoditiesDF = pd.DataFrame(records)
            commoditiesDF.drop(commoditiesDF.tail(1).index,inplace=True)

            high = commoditiesDF['high']
            low = commoditiesDF['low']
            close = commoditiesDF['close']

            supertrend = ta.supertrend(high=high, 
                      low=low, 
                      close=close, 
                      length=7,
                      multiplier=3).iloc[:,0]

            supertrend = supertrend.to_frame()
            supertrend = supertrend.set_axis(["supertrend"], axis=1)
        
            # add supertrend to commodities df
            commoditiesDF = pd.concat([commoditiesDF,supertrend],axis=1)

            commoditiesDF = commoditiesDF.rename(columns={'high': 'High', 'low': 'Low'})
            i= Indicators(commoditiesDF)
            i.alligator()
            commoditiesDF = i.df
            commoditiesDF = commoditiesDF.rename(columns={'High': 'high', 'Low': 'low'})

            # Convert date type to excel supported date type
            commoditiesDF['date'] = commoditiesDF['date'].apply(lambda a: pd.to_datetime(a).date())
            commoditiesDF.to_excel(self.REPORT_FILE_NAME)

            # checking supertrend buy sell conditon
            # Buy Condition

            # to analyse this first we fetch last candle
            triggeredCandle = commoditiesDF.iloc[-1]
            
            # Fetch open,close,high,low
            triggeredCandleOpen = triggeredCandle['open']
            triggeredCandleClose = triggeredCandle['close']
            triggeredCandleHigh = triggeredCandle['high']
            triggeredCandleLow = triggeredCandle['low']

            # Fetch alligator jaw and supertrend
            triggeredCandleSupertrend = triggeredCandle['supertrend']
            triggeredCandleAlligatorJaw = triggeredCandle['alligator_jaws']

            # Now check triggered candle super trend is green or not
            if triggeredCandleClose > triggeredCandleSupertrend:
                logString = 'SUPER_TREND : GREEN'
                self.sendLogReport(logString)

                # Now Check Alligator Jaw Condition 
                # Alligator Jaw must cross the body of candle
                # Means Alligator Jaw line must be between triggered candle open and close
                # Thinking Candle would be bullish

                if triggeredCandleAlligatorJaw > triggeredCandleOpen and triggeredCandleAlligatorJaw < triggeredCandleClose:
                    logString ='TRIGGER CANDLE FOUND : BUY SIGNAL'
                    self.sendLogReport(logString)
                    logString ='Please wait , now looking for trade ... '
                    self.sendLogReport(logString)

                    # check for trade
                    NEED_TO_EXIT_TRADE_LOOP = False
                    while not NEED_TO_EXIT_TRADE_LOOP:
                        now = datetime.now()
                        now = now.astimezone(self.tz)

                        if timeInterval == 1:
                            if now.second == 0:
                                NEED_TO_EXIT_TRADE_LOOP = True
                        else:
                            if now.second == 0 and now.minute % int(timeInterval) == 0:
                                NEED_TO_EXIT_TRADE_LOOP = True
                        
                        symbol = "MCX:{}".format(str(self.tokens[token]))
                        ltp = self.kite.ltp([symbol])
                        latestPrice = ltp[symbol]['last_price']

                        # To make a trade 
                        # ltp must cross high of the triggered candle

                        if latestPrice > triggeredCandleHigh:
                            # Place Order
                            order_id = 'TEST_GOLD_BUY_1234'

                            # Send log about trade executed time
                            tradeExecutedTime ='%02d-%02d-%02d  %02d:%02d' % (now.day,now.month,now.year,now.hour,now.minute)
                            logString = 'TRADE EXECUTED At : ' + str(tradeExecutedTime)
                            self.sendLogReport(logString)

                            # Print log report to console
                            logString = '***************************'
                            self.sendLogReport(logString)
                            logString ='TRADINGSYMBOL : ' + str(self.tokens[token])
                            self.sendLogReport(logString)
                            logString ='***************************'
                            self.sendLogReport(logString)
                            logString ='# BUY SIGNAL #'
                            self.sendLogReport(logString)
                            logString ='ORDER ID : ' + str(order_id)
                            self.sendLogReport(logString)
                            logString ='CLOSE PRICE : ' + str(round(triggeredCandleClose,2))
                            self.sendLogReport(logString)
                            logString ='STOP LOSS : ' + str(round(triggeredCandleLow,2))
                            self.sendLogReport(logString)

                            # generating log
                            # creating dictonary 
                            logDict = {'date':str(tradeExecutedTime),
                            'tradingsymbol':self.tokens[token],
                            'order_id':order_id,
                            'open': round(triggeredCandleOpen,2),
                            'close':round(triggeredCandleClose,2),
                            'high':round(triggeredCandleHigh,2),
                            'low':round(triggeredCandleLow,2),
                            'signal':'BUY',
                            'stop_loss':round(triggeredCandleLow,2)}
                
                            self.commoditiesLogList.append(logDict)
                            logDF = pd.DataFrame(self.commoditiesLogList)
                
                            log = pd.concat([commoditiesLogDF,logDF],axis=1)
                            log.to_excel(self.LOG_FILE_NAME)

                            NEED_TO_EXIT_TRADE_LOOP = True
                            isTraded = True

            # Now check triggered candle super trend is red or not
            elif triggeredCandleSupertrend > triggeredCandleClose:
                logString = 'SUPER_TREND : RED'
                self.sendLogReport(logString)

                # Now Check Alligator Jaw Condition 
                # Alligator Jaw must cross the body of candle
                # Means Alligator Jaw line must be between triggered candle open and close
                # Thinking Candle would be bearish

                if triggeredCandleOpen > triggeredCandleAlligatorJaw and triggeredCandleClose < triggeredCandleAlligatorJaw:
                    logString ='TRIGGER CANDLE FOUND : SELL SIGNAL'
                    self.sendLogReport(logString)
                    logString ='Please wait , now looking for trade ... '
                    self.sendLogReport(logString)

                    # check for trade
                    NEED_TO_EXIT_TRADE_LOOP = False
                    while not NEED_TO_EXIT_TRADE_LOOP:
                        now = datetime.now()
                        now = now.astimezone(self.tz)

                        if timeInterval == 1:
                            if now.second == 0:
                                NEED_TO_EXIT_TRADE_LOOP = True
                        else:
                            if now.second == 0 and now.minute % int(timeInterval) == 0:
                                NEED_TO_EXIT_TRADE_LOOP = True
                        
                        symbol = "MCX:{}".format(str(self.tokens[token]))
                        ltp = self.kite.ltp([symbol])
                        latestPrice = ltp[symbol]['last_price']

                        # To make a trade 
                        # ltp must cross low of the triggered candle

                        if latestPrice < triggeredCandleLow:
                            # Place Order
                            order_id = 'TEST_GOLD_SELL_1234'

                            # Send log about trade executed time
                            tradeExecutedTime ='%02d-%02d-%02d  %02d:%02d' % (now.day,now.month,now.year,now.hour,now.minute)
                            logString = 'TRADE EXECUTED At : ' + str(tradeExecutedTime)
                            self.sendLogReport(logString)

                            logString = '***************************'
                            self.sendLogReport(logString)
                            logString ='TRADINGSYMBOL : ' + str(self.tokens[token])
                            self.sendLogReport(logString)
                            logString ='***************************'
                            self.sendLogReport(logString)
                            logString ='# SELL SIGNAL #'
                            self.sendLogReport(logString)
                            logString ='ORDER ID : ' + str(order_id)
                            self.sendLogReport(logString)
                            logString ='CLOSE PRICE : ' + str(round(triggeredCandleClose,2))
                            self.sendLogReport(logString)
                            logString ='STOP LOSS : ' + str(round(triggeredCandleHigh,2))
                            self.sendLogReport(logString)

                            # generating log
                            # creating dictonary
                            logDict = {'date':str(tradeExecutedTime),
                            'tradingsymbol':self.tokens[token],
                            'order_id':order_id,
                            'open': round(triggeredCandleOpen,2),
                            'close':round(triggeredCandleClose,2),
                            'high':round(triggeredCandleHigh,2),
                            'low':round(triggeredCandleLow,2),
                            'signal':'SELL',
                            'stop_loss':round(triggeredCandleHigh,2)}
                
                            self.commoditiesLogList.append(logDict)
                            logDF = pd.DataFrame(self.commoditiesLogList)
                
                            log = pd.concat([commoditiesLogDF,logDF],axis=1)
                            log.to_excel(self.LOG_FILE_NAME)

                            NEED_TO_EXIT_TRADE_LOOP = True
                            isTraded = True

            if not isTraded:
                logString ='TRADINGSYMBOL : ' + str(self.tokens[token])
                self.sendLogReport(logString)
                logString ='CLOSE PRICE : ' + str(round(triggeredCandleClose,2))
                self.sendLogReport(logString)
                logString = "SUPERTREND VALUE : " + str(round(triggeredCandleSupertrend,2))
                self.sendLogReport(logString)
                logString = "ALLIGATOR JAW VALUE : " + str(round(triggeredCandleAlligatorJaw,2))
                self.sendLogReport(logString)
                logString = '----------------------------------'
                self.sendLogReport(logString)
    
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

        logData = {"logReport" : logString,"selected_commodities":1}

        print(logString)
        self.socketio.emit('log_report',logData)