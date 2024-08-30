from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timezone, timedelta
import pandas as pd

# setting API properties
API_KEY = 'PK2I5CCKUGXSDUMF5729'
API_SECRET = 'R2ETLhRBNHgsFWeI9VfLhT0cijt6hBi0giUuM0jx'
BASE_URL = 'https://paper-api.alpaca.markets/v2'

# initialize the trading and data clients
trading_client = TradingClient(API_KEY,API_SECRET, paper=True)
data_client = CryptoHistoricalDataClient(API_KEY,API_SECRET)

# Define the symbol for Bitcoin and the exchange
symbol = 'BTC/USD'

# Create timezone-aware start and end times
now = datetime.now(timezone.utc)
start_time = (now - timedelta(minutes=30)).isoformat()

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
    print(f"The current price of Bitcoin (BTC) is: ${df.iloc[-1].close} at {df.index.get_level_values('timestamp')[-1]} which is a {round((df.iloc[-1].close-df.iloc[0].close)*100/df.iloc[0].close,2)}% variance from {df.index.get_level_values('timestamp')[0]}")

except Exception as e:
    print(f"Error: {e}")

# Set up schedule to execute bot

import time
    