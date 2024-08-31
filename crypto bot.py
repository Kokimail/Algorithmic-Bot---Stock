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
    m_1 = 15+3 #set minutes delta
    m_2 = m_1*2 #set minutes delta x2
    now = datetime.now(timezone.utc)
    start_time_1 = (now - timedelta(minutes=m_1)).isoformat() #15 minutes ago
    start_time_2 = (now - timedelta(minutes=m_2)).isoformat() #30 minutes ago

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
        end = now.isoformat()
    )

    # Fetch the bar data
    try:
        bars_1 = data_client.get_crypto_bars(bar_request_1)
        bars_2 = data_client.get_crypto_bars(bar_request_2)

        df_1 = pd.DataFrame(bars_1.df)
        df_2 = pd.DataFrame(bars_2.df)

        delay_1 = ((df_1.index.get_level_values('timestamp')[-1] - df_1.index.get_level_values('timestamp')[0]).total_seconds())/60
        delay_2 = ((df_2.index.get_level_values('timestamp')[-1] - df_2.index.get_level_values('timestamp')[0]).total_seconds())/60

        return_1 = (df_1.iloc[-1].close-df_1.iloc[0].close)*100/df_1.iloc[0].close #return from the last m mins
        return_2 = (df_2.iloc[-1].close-df_2.iloc[0].close)*100/df_2.iloc[0].close #return from the last m x 2 mins
        print(f"""The current price of Bitcoin (BTC) is: ${df_1.iloc[-1].close} at {df_1.index.get_level_values('timestamp')[-1]} 
              {round(return_1,2)}% variance from {round(delay_1)} mins ago at {df_1.index.get_level_values('timestamp')[0]}
              {round(return_2,2)}% variance from {round(delay_2)} mins ago at {df_2.index.get_level_values('timestamp')[0]}""")
        print("Bot executed at", time.ctime())
    except Exception as e:
        print(f"Error: {e}")

execute_bot()

# Set up schedule to execute bot

#while True:
    #execute_bot()
    #time.sleep(1800) #sleep for 1800 seconds (30 minutes)

# ctrl + c on terminal to break the loop