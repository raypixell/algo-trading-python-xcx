from kiteconnect import KiteConnect
from datetime import datetime,timedelta
import calendar
import pytz
import os

tz = pytz.timezone('Asia/Kolkata')

api_key = '9fua69n6l7whujs5'
access_token = 'CAou8OlEuZWpVyqB8KSweht61mfT5N6w'

kite = KiteConnect(api_key=api_key,timeout=20)
kite.set_access_token(access_token)

# tokens ={18257666 : 'BANKNIFTY21DECFUT'}
# tokens ={59844359 : 'GOLDM22JANFUT'}
# for token in tokens:
#     symbol = "MCX:{}".format(str(tokens[token]))
#     print(symbol)
#     ltp = kite.ltp([symbol])
#     print(ltp)
#     print(ltp[symbol]['last_price'])

# instrumentList =kite.instruments(exchange="NFO")

# for instrument in instrumentList:
#     now = datetime.now()
#     now = now.astimezone(tz)
#     NIFTY_FILE_NAME = "bank_nifty_instrument_nfo_" + '%02d-%02d-%02d.txt' % (now.day,now.month,now.year)

#     logString = str(instrument['tradingsymbol']) + ' : ' + str(instrument['instrument_token'])

#     # write logReport to txt file
#     f=open(NIFTY_FILE_NAME, "a+")
#     filesize = os.path.getsize(NIFTY_FILE_NAME)
#     if filesize == 0:
#         f.write(logString)
#     else:
#         f.write('\n'+logString)
        
#     # close file stream
#     f.close()

#     print(logString)

# -------------------------------------------------------------------------------
def roundup(x):
    return x if x % 100 == 0 else x + 100 - x % 100

high = 34801.95
roundupNum = roundup(int(high))
if (roundupNum - int(high)) > 50:
    strikePrice = roundupNum
else:
    strikePrice = roundupNum + 100

month = calendar.monthcalendar(datetime.today().year, datetime.today().month)
today = datetime.today().day

thursday = None
options_token = None

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
                options_token = 'BANKNIFTY21DEC{}CE'.format(strikePrice)
            else:
                options_token = 'BANKNIFTY21D{}{}CE'.format(thursday).format(strikePrice)
            
            print(options_token)
            break

else:
    lastThursday = month[-1][calendar.THURSDAY]
    print('lastThursday : {}'.format(lastThursday))

    for i in range(len(month)):
        thursday = month[i][calendar.THURSDAY]
        if thursday > today :
            if (thursday == lastThursday):
                options_token = 'BANKNIFTY21DEC{}CE'.format(strikePrice)
            else:
                options_token = 'BANKNIFTY21D{}{}CE'.format(thursday).format(strikePrice)
            
            print(options_token)
            break

instrumentList =kite.instruments(exchange="NFO")
for instrument in instrumentList:
    tradingSymbol = str(instrument['tradingsymbol'])
    if options_token == tradingSymbol:
        print('------------------------')
        # print('TRADING SYMBOL : {}'.format(tradingSymbol))
        # symbol = "NFO:{}".format(tradingSymbol)
        # ltp = kite.ltp([symbol])
        # print('LAST PRICE : {}'.format(ltp[symbol]['last_price']))
        print(instrument)

        break

print('------------------------')

# input = [1,-2,4,-5,1]
# need_to_terminate = False
# subArray = []
# x=0 
# y=0

# while not need_to_terminate :

#     arr = []
#     sum =0
#     for i in range(x,y):
#         data = input[i]
#         sum+=data
#         arr.append(data)

#     if sum < 0:
#         subArray.append(arr)

#     if y == len(input):
#         if x == len(input):
#             need_to_terminate = True
#         else:
#             x+=1
#             y=0
#     else:
#         y+=1

# print('Total Sub array found whose sum was negative : {}'.format(len(subArray)))
# print('Negative Sub array was : {}'.format(subArray))







    



    
    
    