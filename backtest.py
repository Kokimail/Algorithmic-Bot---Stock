from alpaca.trading.client import TradingClient
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
start_date = '2024-01-01T00:00Z'
end_date = '2024-01-01T23:59:59Z'

# Fetch historical data
test_bar_request = CryptoBarsRequest(
    symbol_or_symbols=symbol,
    timeframe=TimeFrame.Minute,
    start=start_date,
    end=end_date    
)

test_bars = data_client.get_crypto_bars(test_bar_request)

# Convert data to DataFrame
df = pd.DataFrame(test_bars.df)

# Generate a complete datetime index from start to finish at one-minute intervals
start = df.index.get_level_values('timestamp').min()
end = df.index.get_level_values('timestamp').max()
complete_index = pd.date_range(start=start, end=end, freq = 'T') # 'T' for minute frequency

# Reindex btc_df using complete time index
btc_df = df.loc['BTC/USD']
btc_df_reindexed = btc_df.reindex(complete_index)

# Interpolate missing values linearly
df_interpolated = btc_df_reindexed.interpolate(method='linear')

# Resample data to 15-minute intervals
df_15m = df_interpolated.resample('15T').agg({
    'open': 'first',
    'high': 'first',
    'low': 'first',
    'close': 'first',
    'volume': 'first'
})

df_15m['close_change'] = df_15m['close'].diff()
df_15m['return'] = df_15m['close'].pct_change()

print(df_15m)

# Simulating trading
investment = 1000
