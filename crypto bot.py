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
    now = datetime.now(timezone.utc)
    start_time = (now - timedelta(minutes=60)).isoformat()

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

        # Generate a complete datetime index from start to finish at one-minute intervals
        start = df.index.get_level_values('timestamp').min()
        end = df.index.get_level_values('timestamp').max()
        complete_index = pd.date_range(start=start, end=end, freq = 'T') # 'T' for minute frequency

        # Reindex btc_df using complete time index
        btc_df = df.loc['BTC/USD']
        btc_df_reindexed = btc_df.reindex(complete_index)

        # Interpolate missing values linearly
        df_interpolated = btc_df_reindexed.interpolate(method='linear')

        # Pulls index (timestamp) from m minutes ago
        m = 15
        delay_1 = df_interpolated.index[-1] - timedelta(minutes=m)
        delay_2 = df_interpolated.index[-1] - timedelta(minutes=m*2)

        # Set returns
        return_1 = (df_interpolated.iloc[-1].close-df_interpolated.loc[delay_1].close)*100/df_interpolated.loc[delay_1].close #return from the last m mins
        return_2 = (df_interpolated.loc[delay_1].close-df_interpolated.loc[delay_2].close)*100/df_interpolated.loc[delay_2].close #return from m x 2 mins ago to return_1

        print(f"""The current price of Bitcoin (BTC) is: ${df_interpolated.iloc[-1].close} at {df_interpolated.index[-1]} 
              {round(return_1,2)}% variance from {m} mins ago at {delay_1}
              {round(return_2,2)}% variance from {m*2} to {m} mins ago at {delay_2}""")
        
        # Execute buy, sell, pass
        if return_1 > 0 and return_2 > 0:
            print("buy")
        elif return_1 < 0 and return_2 < 0:
            print("sell")
        else:
            print("pass")

        print("Bot executed at", time.ctime())
    except Exception as e:
        print(f"Error: {e}")

execute_bot()

# Set up schedule to execute bot

#while True:
    #execute_bot()
    #time.sleep(1800) #sleep for 1800 seconds (30 minutes)

# ctrl + c on terminal to break the loop