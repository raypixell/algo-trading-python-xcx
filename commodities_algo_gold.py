# -*- coding: utf-8 -*-
"""
Created on Tue Oct 12 13:07:04 2021

@author: XCS
"""

from kiteconnect import KiteConnect
from datetime import datetime,timedelta
import account_config
import pandas as pd
import pandas_ta as ta
from tapy import Indicators
import time



access_token=account_config.getAccessToken()
api_key=account_config.getApiKey()

kite = KiteConnect(api_key=api_key,timeout=20)
kite.set_access_token(access_token)
print('Successfully logged in Kite API!')

global commoditiesLogDF
global commoditiesLogList
LOG_FILE_NAME = 'commodities_log_gold.xlsx'
REPORT_FILE_NAME = 'commodities_gold.xlsx'
SCRIPT_COMMENT = 'Please wait while checking " GOLD " commodities...'
commoditiesLogList = []


candleInterval = '15minute'
no_of_days_for_candle_data = 30
quantity = 1

# Define Range to date
# By Default it is hard coded set for 60 days
from_date = datetime.strftime(datetime.now() - timedelta(no_of_days_for_candle_data),"%Y-%m-%d")
to_date = datetime.today().strftime('%Y-%m-%d')

tokens ={59089671 : 'GOLDPETAL21OCTFUT'}



def startCommoditiesAlgo():
    from datetime import datetime,timedelta
    while True:
        if datetime.now().second == 0 and datetime.now().minute % 15 == 0:
            try:
                print('start checking at : ' , datetime.now())
                checkComodities()
            except Exception as ex:
                print(ex)
                checkComodities()


    
def checkComodities():
    
    try:
        commoditiesLogDF = pd.read_excel(LOG_FILE_NAME)
    except Exception as ex:
        print(ex)
        commoditiesLogDF = pd.DataFrame()
        commoditiesLogDF.to_excel(LOG_FILE_NAME)
    
    print(SCRIPT_COMMENT)
    isTraded = False
    for token in tokens:
        records = kite.historical_data(token, 
                    from_date=from_date, 
                    to_date=to_date, 
                    interval=candleInterval)
        
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
        commoditiesDF.to_excel(REPORT_FILE_NAME)
        
        # checking supertrend buy sell conditon
        # Buy Condition
        
        # to analyse this first we fetch last candle
        lastCandle = commoditiesDF.iloc[-1]
        lastCandleClose = lastCandle['close']
        lastCandleSupertrend = lastCandle['supertrend']
        
        secondLastCandle = commoditiesDF.iloc[-2]
        secondLastCandleClose = secondLastCandle['close']
        secondLastCandleOpen = secondLastCandle['open']
        secondLastCandleHigh = secondLastCandle['high']
        secondLastCandleLow = secondLastCandle['low']
        secondLastAligatorJaw = secondLastCandle['alligator_jaws']
        
        if lastCandleClose > lastCandleSupertrend:
            print('Supertrend : GREEN')
            # check alligator jaw
            # case 1 :
            # alligator jaw must cross the body of candle
            # alligator jaw must be between candle open and close
            # case 2 :
            # then we can buy on high of second last candle
            # means last candle close must be equat to or greater than secondlast candle high
            # stop loss = last candle low
            
            
            if ((secondLastCandleOpen < secondLastAligatorJaw) and (secondLastCandleClose > secondLastAligatorJaw)) and (lastCandleClose >= secondLastCandleHigh):
                isTraded = True
                
                order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                exchange ='MCX' ,
                                tradingsymbol =tokens[token],
                                transaction_type = kite.TRANSACTION_TYPE_BUY,
                                quantity = quantity,
                                product = 'MIS', 
                                order_type = 'MARKET',
                                tag='XCS')
                
                print('***************************')
                print('TRADINGSYMBOL : ' , tokens[token])
                print('***************************')
                print('BUY SIGNAL : ')
                print('ORDER ID : ' , order_id)
                print('CLOSE PRICE : ' , lastCandle['close'])
                print('STOP LOSS : ' , lastCandle['low'])
                
                # generating log
                # creating dictonary 
                logDict = {'date':datetime.now(),
                            'tradingsymbol':tokens[token],
                            'order_id':order_id,
                            'open': lastCandle['open'],
                            'close':lastCandle['close'],
                            'high':lastCandle['high'],
                            'low':lastCandle['low'],
                            'signal':'BUY',
                            'stop_loss':lastCandle['low']}
                
                commoditiesLogList.append(logDict)
                logDF = pd.DataFrame(commoditiesLogList)
                
                log = pd.concat([commoditiesLogDF,logDF],axis=1)
                log.to_excel(LOG_FILE_NAME)
                
        elif lastCandleSupertrend > lastCandleClose:
            print('Supertrend : RED : SELL')
            # check aligator jaw
            # case 1 :
            # alligator jaw must cross the body of candle
            # alligator jaw must be between candle open and close
            # case 2 :
            # then we can sell on low of second last candle
            # means last candle close must be equat to or less than secondlast candle high
            # stop loss = last candle high
            if ((secondLastCandleOpen > secondLastAligatorJaw) and (secondLastCandleClose < secondLastAligatorJaw)) and (lastCandleClose <= secondLastCandleLow):
                isTraded = True
                
                order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                exchange ='MCX' ,
                                tradingsymbol =tokens[token],
                                transaction_type = kite.TRANSACTION_TYPE_SELL,
                                quantity = quantity,
                                product = 'MIS', 
                                order_type = 'MARKET',
                                tag='XCS')
                
                print('***************************')
                print('TRADINGSYMBOL : ' , tokens[token])
                print('***************************')
                print('SELL SIGNAL : ')
                print('ORDER ID : ' , order_id)
                print('CLOSE PRICE : ' , lastCandle['close'])
                print('STOP LOSS : ' , lastCandle['high'])
                
                # generating log
                # creating dictonary 
                logDict = {'date':datetime.now(),
                            'tradingsymbol':tokens[token],
                            'order_id':order_id,
                            'open': lastCandle['open'],
                            'close':lastCandle['close'],
                            'high':lastCandle['high'],
                            'low':lastCandle['low'],
                            'signal':'SELL',
                            'stop_loss':lastCandle['high']}
                
                commoditiesLogList.append(logDict)
                logDF = pd.DataFrame(commoditiesLogList)
                
                log = pd.concat([commoditiesLogDF,logDF],axis=1)
                log.to_excel(LOG_FILE_NAME)
                
        
        time.sleep(1)
        
    if not isTraded:
        print('No trade this session...')
        print('--------End-----------')
    else:
        print('----------------------------------')   
    
    

if __name__ == "__main__":
    # check commodities
    startCommoditiesAlgo()
        
        
        
        
        
        