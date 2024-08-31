
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timezone, timedelta
import pandas as pd
from alpaca.data.requests import CryptoBarsRequest

symbol = 'BTC/USD' 

m = 30 #set minutes delta
mh = m//2 #set halftime
now = datetime.now(timezone.utc)
start_time_1 = (now - timedelta(minutes=mh)).isoformat() #15 minutes ago
start_time_2 = (now - timedelta(minutes=m)).isoformat() #30 minutes ago

print(now)
print(start_time_1)
print(start_time_2)
print(timedelta(minutes=mh))
print(timedelta(minutes=m))
print(now)
print(now-timedelta(minutes=mh))
print(now-timedelta(minutes=m))

    # Create a request for the latest minute bar for Bitcoin
bar_request_1 = CryptoBarsRequest(
    symbol_or_symbols=symbol,
    timeframe=TimeFrame.Minute,
    start= start_time_1,
    end = now.isoformat()
)

bar_request_2 = CryptoBarsRequest(
    symbol_or_symbols=symbol,
    timeframe=TimeFrame.Minute,
    start= start_time_2,
    end = start_time_1
)

print(bar_request_1)
print(bar_request_2)