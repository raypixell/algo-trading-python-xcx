from kiteconnect import KiteConnect,KiteTicker
from datetime import datetime,timedelta
import pandas as pd
import time as tm
import calendar
import json
import pytz
import os

tz = pytz.timezone('Asia/Kolkata')
api_key = '9fua69n6l7whujs5'
access_token = '9JR10GlUbTcKSzEhrEz43laWdhwWysUW'

kite = KiteConnect(api_key=api_key,timeout=20)
kite.set_access_token(access_token)

kws = KiteTicker(api_key, access_token)

now = datetime.now()
now = now.astimezone(tz)
# today = now.day

# month = calendar.monthcalendar(now.year, now.month)

# for week in month:
      
#     if today in week:     
#         saturday = week[calendar.SATURDAY]
#         sunday = week[calendar.SUNDAY]
#         print('today : ',today,'saturday : ',saturday,'sunday : ' , sunday)

#         if today == saturday or today == sunday:
#             print('MARKET CLOSED')
#         else:
#             print('TRADING DAY')
#             if now.hour==15:
#                 if now.minute>30:
#                     print('MARKET CLOSED')
#             else:
#                 if now.hour >= 16:
#                     print('MARKET CLOSED
# newDate = '%02d-%b-%02d' % (now.day,now.month,now.year)
# executedTill = now + timedelta(minutes=5)
# NEED_TO_EXIT_TRADE_LOOP = False
# while not NEED_TO_EXIT_TRADE_LOOP:
#     now = datetime.now()
#     now = now.astimezone(tz)
                    
#     if now.minute == executedTill.minute :
#         NEED_TO_EXIT_TRADE_LOOP = True
        
#     print('Now : {}'.format(now.minute))
#     print('Executed Till : {}'.format(executedTill.minute))
# -------------------------------------------------------------------------------------
# go 5 minutes into the future

def on_ticks(ws,ticks):
    
    now = datetime.now()
    now = now.astimezone(tz)

    # Now update json file 
    with open("bank_nifty_script_running_status.json", "r") as jsonFile:
        script_running_staus = json.load(jsonFile)

    if now.minute == next5min.minute and script_running_staus["is_trade_executed"]:
        print("Loop Exit At : ",now.minute , now.second)
        kws.unsubscribe([260105])

        # Update Script Running Status
        script_running_staus["is_trade_executed"] = False
        with open("bank_nifty_script_running_status.json", "w") as jsonFile:
            json.dump(script_running_staus, jsonFile)
    else:
        print('LTP 1 : {}'.format(ticks[0]['last_price']))
        

def on_ticks_2(ws,ticks):
    now = datetime.now()
    now = now.astimezone(tz)

    # Now update json file 
    with open("bank_nifty_script_running_status.json", "r") as jsonFile:
        script_running_staus = json.load(jsonFile)

    if now.minute == next5min.minute and script_running_staus["is_trade_executed"]:
        print("Loop Exit At : ",now.minute , now.second)
        kws.unsubscribe([260105])

        # Update Script Running Status
        script_running_staus["is_trade_executed"] = False
        with open("bank_nifty_script_running_status.json", "w") as jsonFile:
            json.dump(script_running_staus, jsonFile)
    else:
        print('LTP 2 : {}'.format(ticks[0]['last_price']))
        

def on_connect(ws,response):
    ws.set_mode(ws.MODE_LTP, [260105])

interval = 5
now = datetime.now()
now = now.astimezone(tz)

later5min = now + timedelta(0,0,0,0,int(interval))
# round to 5 minutes
next5min = datetime(later5min.year, later5min.month, later5min.day, later5min.hour, int(interval)*int(later5min.minute/int(interval)), 0, 0)
print("Next 5 Min : ",next5min.hour,":",next5min.minute)

# Now update json file 
with open("bank_nifty_script_running_status.json", "r") as jsonFile:
    script_running_staus = json.load(jsonFile)

# Update Script Running Status
script_running_staus["is_trade_executed"] = True
with open("bank_nifty_script_running_status.json", "w") as jsonFile:
    json.dump(script_running_staus, jsonFile)

kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.connect(threaded=True)

while script_running_staus["is_trade_executed"]:
    # Now update json file 
    with open("bank_nifty_script_running_status.json", "r") as jsonFile:
        script_running_staus = json.load(jsonFile)

    if kws.is_connected() and script_running_staus["is_trade_executed"]:
        kws.set_mode(kws.MODE_LTP, [260105])
        
    tm.sleep(0.5)

tm.sleep(60)

kws.on_ticks = on_ticks_2
 
interval = 5
now = datetime.now()
now = now.astimezone(tz)

later5min = now + timedelta(0,0,0,0,int(interval))
# round to 5 minutes
next5min = datetime(later5min.year, later5min.month, later5min.day, later5min.hour, int(interval)*int(later5min.minute/int(interval)), 0, 0)
print("Next 5 Min : ",next5min.hour,":",next5min.minute)

# Update Script Running Status
script_running_staus["is_trade_executed"] = True
with open("bank_nifty_script_running_status.json", "w") as jsonFile:
    json.dump(script_running_staus, jsonFile)

while script_running_staus["is_trade_executed"]:

    # Now update json file 
    with open("bank_nifty_script_running_status.json", "r") as jsonFile:
        script_running_staus = json.load(jsonFile)

    if kws.is_connected() and script_running_staus["is_trade_executed"]:
        kws.set_mode(kws.MODE_LTP, [260105])
    
    tm.sleep(0.5)








            