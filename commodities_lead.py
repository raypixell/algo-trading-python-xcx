from kiteconnect import KiteConnect
from datetime import datetime,timedelta
import pandas as pd
import pandas_ta as ta
from tapy import Indicators
import time
import json
import logging
import os
import pytz


class LeadCommodities:

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

    TERMINATE_LEAD = None

    def __init__(self,socketio,selectedInterval):

        self.socketio = socketio
        self.TERMINATE_LEAD = False

        # Api key and access token
        with open('access_token.json', 'r') as openfile:
            accessTokenObj = json.load(openfile)
            self.access_token = accessTokenObj['access_token']

        self.api_key='9fua69n6l7whujs5'

        # Log file name
        now = datetime.now()
        now = now.astimezone(self.tz)
        self.DOWNLOAD_LOG_FILE_NAME = "lead_" + '%02d-%02d-%02d.txt' % (now.day,now.month,now.year)
        print(self.DOWNLOAD_LOG_FILE_NAME)

        # Log file name
        self.LOG_FILE_NAME = 'commodities_log_lead.xlsx'
        self.REPORT_FILE_NAME = 'commodities_lead.xlsx'
        self.SCRIPT_COMMENT = 'Please wait while checking " LEAD " commodities...'
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
        self.tokens ={59423239 : 'LEAD21DECFUT'}

    def getAccessToken(self):
        return self.access_token

    def loginKite(self):
        self.kite = KiteConnect(api_key=self.api_key,timeout=20)
        self.kite.set_access_token(self.access_token)

        self.logMessage = 'Lead Script Started...'
        self.sendLogReport(self.logMessage)
        self.logMessage = 'Script automatically executed at an interval of ' +"' " +self.candleInterval+" '"
        self.sendLogReport(self.logMessage)

    def stopThread(self):
        print('stopThread called....')
        self.TERMINATE_LEAD = True

    def startCommoditiesAlgo(self,timeInterval):

        self.TERMINATE_LEAD = False
        
        try:
            while not self.TERMINATE_LEAD:
                now = datetime.now()
                now = now.astimezone(self.tz)

                if timeInterval == 1:
                    if now.second == 0:
                        self.currentTime ='%02d-%02d-%02d  %02d:%02d' % (now.day,now.month,now.year,now.hour,now.minute)
                        logString = 'start checking at : ' + str(self.currentTime)
                        self.sendLogReport(logString)

                        # Now Checking Commodities
                        time.sleep(1)
                        self.checkComodities()
                    
                elif timeInterval == 5:
                    if now.second == 0 and now.minute % 5 == 0:
                        self.currentTime ='%02d-%02d-%02d  %02d:%02d' % (now.day,now.month,now.year,now.hour,now.minute)
                        logString = 'start checking at : ' + str(self.currentTime)
                        self.sendLogReport(logString)

                        # Now Checking Commodities
                        time.sleep(1)
                        self.checkComodities()
                
                elif timeInterval == 10:
                    if now.second == 0 and now.minute % 10 == 0:
                        self.currentTime ='%02d-%02d-%02d  %02d:%02d' % (now.day,now.month,now.year,now.hour,now.minute)
                        logString = 'start checking at : ' + str(self.currentTime)
                        self.sendLogReport(logString)

                        # Now Checking Commodities
                        time.sleep(1)
                        self.checkComodities()
                
                elif timeInterval == 15:
                    if now.second == 0 and now.minute % 15 == 0:
                        self.currentTime ='%02d-%02d-%02d  %02d:%02d' % (now.day,now.month,now.year,now.hour,now.minute)
                        logString = 'start checking at : ' + str(self.currentTime)
                        self.sendLogReport(logString)

                        # Now Checking Commodities
                        time.sleep(1)
                        self.checkComodities()
                
                elif timeInterval == 30:
                    if now.second == 0 and now.minute % 30 == 0:
                        self.currentTime ='%02d-%02d-%02d  %02d:%02d' % (now.day,now.month,now.year,now.hour,now.minute)
                        logString = 'start checking at : ' + str(self.currentTime)
                        self.sendLogReport(logString)

                        # Now Checking Commodities
                        time.sleep(1)
                        self.checkComodities()
                           
        except Exception as ex:
            logString = str(ex)
            self.sendLogReport(logString)
            self.socketio.emit('force_stop_script',4)

    def checkComodities(self):
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
            # commoditiesDF.drop(commoditiesDF.tail(1).index,inplace=True)

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
            lastCandle = commoditiesDF.iloc[-1]
            lastCandleClose = lastCandle['close']
            lastCandleSupertrend = lastCandle['supertrend']
            lastCandleAlligatorJas = lastCandle['alligator_jaws']
        
            secondLastCandle = commoditiesDF.iloc[-2]
            secondLastCandleClose = secondLastCandle['close']
            secondLastCandleOpen = secondLastCandle['open']
            secondLastCandleHigh = secondLastCandle['high']
            secondLastCandleLow = secondLastCandle['low']
            secondLastAligatorJaw = secondLastCandle['alligator_jaws']

            if lastCandleClose > lastCandleSupertrend:
                logString = 'SUPER_TREND : GREEN'
                self.sendLogReport(logString)

                # check alligator jaw
                # -------------------
                # case 1 :
                # -------------------
                # alligator jaw must cross the body of candle
                # alligator jaw must be between candle open and close
                # -------------------
                # case 2 :
                # -------------------
                # then we can buy on high of second last candle
                # means last candle close must be equat to or greater than secondlast candle high
                # stop loss = last candle low

                if ((secondLastCandleOpen < secondLastAligatorJaw) and (secondLastCandleClose > secondLastAligatorJaw)) and (lastCandleClose >= secondLastCandleHigh):
                    isTraded = True

                    order_id = self.kite.place_order(variety=self.kite.VARIETY_REGULAR,
                            exchange ='MCX' ,
                            tradingsymbol =self.tokens[token],
                            transaction_type = self.kite.TRANSACTION_TYPE_BUY,
                            quantity = self.quantity,
                            product = 'MIS', 
                            order_type = 'SL-M',
                            trigger_price = str(round(secondLastCandleLow,2)),
                            tag='XCS')

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
                    logString ='CLOSE PRICE : ' + str(round(lastCandle['close'],2))
                    self.sendLogReport(logString)
                    logString ='STOP LOSS : ' + str(round(secondLastCandleLow,2))
                    self.sendLogReport(logString)

                    # generating log
                    # creating dictonary 
                    now = datetime.now()
                    now = now.astimezone(self.tz)
                    self.currentTime ='%02d-%02d-%02d  %02d:%02d' % (now.day,now.month,now.year,now.hour,now.minute)
                    logDict = {'date':str(self.currentTime),
                            'tradingsymbol':self.tokens[token],
                            'order_id':order_id,
                            'open': round(lastCandle['open'],2),
                            'close':round(lastCandle['close'],2),
                            'high':round(lastCandle['high'],2),
                            'low':round(lastCandle['low'],2),
                            'signal':'BUY',
                            'stop_loss':round(secondLastCandleLow,2)}
                
                    commoditiesLogList.append(logDict)
                    logDF = pd.DataFrame(commoditiesLogList)
                
                    log = pd.concat([commoditiesLogDF,logDF],axis=1)
                    log.to_excel(self.LOG_FILE_NAME)

            elif lastCandleSupertrend > lastCandleClose:
                logString = 'SUPER_TREND : RED'
                self.sendLogReport(logString)

                # check aligator jaw
                # -------------------
                # case 1 :
                # -------------------
                # alligator jaw must cross the body of candle
                # alligator jaw must be between candle open and close
                # -------------------
                # case 2 :
                # -------------------
                # then we can sell on low of second last candle
                # means last candle close must be equat to or less than secondlast candle high
                # stop loss = last candle high

                if ((secondLastCandleOpen > secondLastAligatorJaw) and (secondLastCandleClose < secondLastAligatorJaw)) and (lastCandleClose <= secondLastCandleLow):
                    isTraded = True

                    order_id = self.kite.place_order(variety=kite.VARIETY_REGULAR,
                            exchange ='MCX' ,
                            tradingsymbol =self.tokens[token],
                            transaction_type = kite.TRANSACTION_TYPE_SELL,
                            quantity = self.quantity,
                            product = 'MIS', 
                            order_type = 'SL-M',
                            trigger_price = str(round(secondLastCandleHigh,2)),
                            tag='XCS')

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
                    logString ='CLOSE PRICE : ' + str(round(lastCandle['close'],2))
                    self.sendLogReport(logString)
                    logString ='STOP LOSS : ' + str(round(secondLastCandleHigh,2))
                    self.sendLogReport(logString)

                    # generating log
                    # creating dictonary 
                    now = datetime.now()
                    now = now.astimezone(self.tz)
                    self.currentTime ='%02d-%02d-%02d  %02d:%02d' % (now.day,now.month,now.year,now.hour,now.minute)
                    logDict = {'date':str(self.currentTime),
                            'tradingsymbol':self.tokens[token],
                            'order_id':order_id,
                            'open': round(lastCandle['open'],2),
                            'close':round(lastCandle['close'],2),
                            'high':round(lastCandle['high'],2),
                            'low':round(lastCandle['low'],2),
                            'signal':'SELL',
                            'stop_loss':round(secondLastCandleHigh,2)}
                
                    commoditiesLogList.append(logDict)
                    logDF = pd.DataFrame(commoditiesLogList)
                
                    log = pd.concat([commoditiesLogDF,logDF],axis=1)
                    log.to_excel(self.LOG_FILE_NAME)

            if not isTraded:
                logString ='TRADINGSYMBOL : ' + str(self.tokens[token])
                self.sendLogReport(logString)
                logString ='CLOSE PRICE : ' + str(round(lastCandle['close'],2))
                self.sendLogReport(logString)
                logString = "SUPERTREND VALUE : " + str(round(lastCandleSupertrend,2))
                self.sendLogReport(logString)
                logString = "ALLIGATOR JAW VALUE : " + str(round(lastCandleAlligatorJas,2))
                self.sendLogReport(logString)
                logString = '----------------------------------'
                self.sendLogReport(logString)

            time.sleep(1)
    
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

        # read the txt file and get content
        f=open(self.DOWNLOAD_LOG_FILE_NAME, "r")
        if f.mode == 'r':
            self.logReport =f.read()
        
        # close file stream
        f.close()

        logData = {"logReport" : logString,"selected_commodities":4}

        print(logString)
        self.socketio.emit('log_report',logData)
                

            
            
        

    
