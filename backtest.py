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
df_15m['previous_return'] = df_15m['return'].shift(1)

print(df_15m)

# Simulating trading
initial_capital = 1000
cash = initial_capital
btc_held = 0
i = -1
t = 0

for index, row in df_15m.iterrows():
    if row['return'] > 0 and row['previous_return'] > 0 and i == -1: # Buy signal
        btc_held = cash / row['close']
        cash = 0 # Invest all cash
        i = i*-1
        t = t+1
    elif row['return'] < 0 and row['previous_return'] < 0 and i == 1: # Sell signal
        cash = btc_held * row['close']
        btc_held = 0 # Sell all holdings
        i = i*-1
        t = t+1
    else:
        pass

final_value = cash if cash > 0 else btc_held * df_15m.iloc[-1]['close']
print(f"Final portfolio value: ${final_value:.2f} from an initial capital of ${initial_capital} with {t} transactions")



