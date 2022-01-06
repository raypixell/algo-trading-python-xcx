from kiteconnect import KiteConnect
from datetime import datetime,timedelta
import pandas as pd
import calendar
import pytz
import os

tz = pytz.timezone('Asia/Kolkata')
api_key = '9fua69n6l7whujs5'
access_token = '5ZuFm0YGpD5jaLfU5rViL2KZYFpRgpb0'

kite = KiteConnect(api_key=api_key,timeout=20)
kite.set_access_token(access_token)

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


            