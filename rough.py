from kiteconnect import KiteConnect
from datetime import datetime,timedelta
import pandas as pd
import calendar
import pytz
import os

tz = pytz.timezone('Asia/Kolkata')
api_key = '9fua69n6l7whujs5'
access_token = 'mZEAL5TbcpZa6924b9QAAKNngzq8yZwS'

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
# -------------------------------------------------------------------------------------
# go 5 minutes into the future
# interval = 5

# later5min = now + timedelta(0,0,0,0,int(interval))
# # round to 5 minutes
# next5min = datetime(later5min.year, later5min.month, later5min.day, later5min.hour, int(interval)*int(later5min.minute/int(interval)), 0, 0)
# print("Next 5 Min : ",next5min.hour,":",next5min.minute)

# EXIT_LOOP = False
# while not EXIT_LOOP:
#     now = datetime.now()
#     now = now.astimezone(tz)

#     if now.minute == next5min.minute:
#         print("Loop Exit At : ",now.minute , now.second)
#         EXIT_LOOP = True

# ----------------------------------------------------------------------------------------
# orderList = kite.orders()
# orderListDf = pd.DataFrame(orderList)
# lastFrame = orderListDf.iloc[-1]
# orderId = lastFrame['order_id']
# print(orderId)


# orderReport = kite.order_trades(orderId)
# orderReportDf = pd.DataFrame(orderReport)
# orderReportDf.to_excel('order_list.xlsx')

# print(orderReport)


symbol = "NFO:{}".format('BANKNIFTY2211337800CE')
print(symbol)
ltp = kite.ltp([symbol])
latestPrice = ltp[symbol]['last_price']
print(latestPrice)

print(str(True))





            