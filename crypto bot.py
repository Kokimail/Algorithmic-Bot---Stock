from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timezone, timedelta
import pandas as pd
import time

# setting API properties
API_KEY = 'PK2I5CCKUGXSDUMF5729'
API_SECRET = 'R2ETLhRBNHgsFWeI9VfLhT0cijt6hBi0giUuM0jx'
BASE_URL = 'https://paper-api.alpaca.markets/v2'

# initialize the trading and data clients
trading_client = TradingClient(API_KEY,API_SECRET, paper=True)
data_client = CryptoHistoricalDataClient(API_KEY,API_SECRET)

# Define the symbol for Bitcoin and the exchange
symbol = 'BTC/USD'

# defining bot

def execute_bot():

    # Create timezone-aware start and end times
    m = 30 #set minutes delta
    mh = m//2 #set halftime
    now = datetime.now(timezone.utc)
    start_time = (now - timedelta(minutes=m)).isoformat()

    print(now)
    print(start_time)

    # Create a request for the latest minute bar for Bitcoin
    bar_request = CryptoBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Minute,
        start= start_time,
        end = now.isoformat()
    )

# Fetch the bar data
    try:
        bars = data_client.get_crypto_bars(bar_request)
        df = pd.DataFrame(bars.df)
        print(df)
        return_1 = (df.iloc[-mh].close-df.iloc[0].close)*100/df.iloc[0].close #return for first half of time table
        return_2 = (df.iloc[-1].close-df.iloc[-mh].close)*100/df.iloc[-mh].close #return for second half of time table
        print(f"The current price of Bitcoin (BTC) was: ${df.iloc[-mh].close} at {df.index.get_level_values('timestamp')[-mh]} which is a {round(return_1,2)}% variance from {df.index.get_level_values('timestamp')[0]}")
        print(f"The current price of Bitcoin (BTC) is: ${df.iloc[-1].close} at {df.index.get_level_values('timestamp')[-1]} which is a {round(return_2,2)}% variance from {df.index.get_level_values('timestamp')[-mh]}")
        print("Bot executed at", time.ctime())
    except Exception as e:
        print(f"Error: {e}")

execute_bot()

# Set up schedule to execute bot

#while True:
    #execute_bot()
    #time.sleep(1800) #sleep for 1800 seconds (30 minutes)

# ctrl + c on terminal to break the loop