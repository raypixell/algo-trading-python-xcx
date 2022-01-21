from kiteconnect import KiteConnect,KiteTicker
from datetime import datetime,timedelta
import pandas as pd
import time as tm
import calendar
import json
import pytz
import os

class KiteTickerTest :

    def __init__(self):
        self.tz = pytz.timezone('Asia/Kolkata')
        self.api_key = '9fua69n6l7whujs5'
        self.access_token = 'yi0uJYTBKozTo1K11uSILe55BGL1EapT'

        self.kite = KiteConnect(api_key=self.api_key,timeout=20)
        self.kite.set_access_token(self.access_token)

        self.kws = KiteTicker(self.api_key, self.access_token)
        

        self.NEED_TO_EXIT_TRADE_LOOP = None

    def on_connect(self,ws,response):
        if not self.NEED_TO_EXIT_TRADE_LOOP:
            print('onConnect : ',[256265])
            ws.subscribe([256265])
            ws.set_mode(ws.MODE_LTP, [256265])
        else:
            print('Handle on_connect : No Need To Start')


    def Test1(self,ws,ticks):
        self.computeTest1(ws,ticks)  

    def computeTest1(self,ws,ticks):
        now = datetime.now()
        now = now.astimezone(self.tz)

        if len(ticks)>0:
            latestPrice = ticks[0]['last_price']
            print('LTP TEST1 : {}'.format(latestPrice))

        if now.minute % 5 == 0:
            self.NEED_TO_EXIT_TRADE_LOOP = True
            print('Web Socket Stopped at : ' , now.hour,':',now.minute)
            ws.unsubscribe([256265])


    def Test2(self,ws,ticks):
        self.computeTest2(ws,ticks)

    def computeTest2(self,ws,ticks):
        now = datetime.now()
        now = now.astimezone(self.tz)

        if len(ticks)>0:
            latestPrice = ticks[0]['last_price']
            print('LTP TEST2 : {}'.format(latestPrice))

        if now.minute % 5 == 0:
            self.NEED_TO_EXIT_TRADE_LOOP = True
            print('Web Socket Stopped at : ' , now.hour,':',now.minute)
            ws.unsubscribe([256265])

    def startLoop(self):
        while True:
            now = datetime.now()
            now = now.astimezone(self.tz)

            if now.minute % 2 == 0 and not now.minute % 5 == 0:
                self.startTicker()

    def startTicker(self):
        self.kws.on_ticks = self.Test1

        try:
            if not self.kws.is_connected():
                self.kws.on_connect = self.on_connect
                self.kws.connect(threaded=True)
        except Exception as e :
            print(e)
            self.kws.on_connect = self.on_connect
            self.kws.connect(threaded=True)

        self.NEED_TO_EXIT_TRADE_LOOP = False

        while not self.NEED_TO_EXIT_TRADE_LOOP :
            if self.kws.is_connected():
                self.kws.set_mode(self.kws.MODE_LTP, [256265])
    
            tm.sleep(0.5)

        self.NEED_TO_EXIT_TRADE_LOOP = False
        print('Now Sleeping for 60s')
        tm.sleep(60)
        print('Starting Socket ')
        self.kws.on_ticks = self.Test2

        while not self.NEED_TO_EXIT_TRADE_LOOP :
            if self.kws.is_connected():
                self.kws.set_mode(self.kws.MODE_LTP, [256265])
    
            tm.sleep(0.5)


if __name__ == '__main__':
    kiteTest = KiteTickerTest()
    kiteTest.startLoop()

            