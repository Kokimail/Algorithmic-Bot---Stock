'''
Multiple Linear Regression
Y = b0 + b1X1 + b2X2 + ... bpXp + e
Y = dependent variable (prediction)
X1, X2,..., Xn = independent variables (predictors)
B0 = Y-intercept of the regression line: expected value of Y when all the X values are 0
B1, B2,..., Bn = coefficients of the independent variables: represents the change in the dependent variable for one unit change in the corresponding independent variable (assuming all other variables are held constant)
e = error: variability in Y that cannot be explained by the linear relationship with the X variables


In our model, these represent:
Y = return
X1 = delay timing
X2 = number of correspondence
X3 = percentage threshold
'''

from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime
import pandas as pd
import time
import numpy as np
import os

# setting API properties
API_KEY = 'PK2I5CCKUGXSDUMF5729'
API_SECRET = 'R2ETLhRBNHgsFWeI9VfLhT0cijt6hBi0giUuM0jx'
BASE_URL = 'https://paper-api.alpaca.markets/v2'

# initialize the trading and data clients
trading_client = TradingClient(API_KEY,API_SECRET, paper=True)
data_client = StockHistoricalDataClient(API_KEY,API_SECRET)

# Set variables to fetch historical data
start_datetime = datetime(2024,1,1)
end_datetime = datetime(2024,6,30)
stock = "META"

test_bar_request = StockBarsRequest(
    symbol_or_symbols = [stock],
    timeframe = TimeFrame.Minute,
    start = start_datetime,
    end = end_datetime
)

test_bars = data_client.get_stock_bars(test_bar_request)

# Convert data to DataFrame
df = pd.DataFrame(test_bars.df)
#print(df)
#df.to_csv('C:/Users/kokik/OneDrive/Documents/GitHub/Algorithmic-Bot/stock_df_raw.csv')


# Set variables to configure backtest
delay_timing = "15T" # 15-minutes intervals
succession = 3 # number of ups/downs in a row for execution
percentage_threshold = 0.000 # percentage threshold for execution

# Generate a complete datetime index from start to finish at one-minute intervals
start = df.index.get_level_values('timestamp').min()
end = df.index.get_level_values('timestamp').max()
complete_index = pd.date_range(start=start, end=end, freq = 'T') # 'T' for minute frequency

# Reindex btc_df using complete time index
stock_df = df.loc[stock]
df_reindexed = stock_df.reindex(complete_index)

# Interpolate missing values linearly
df_interpolated = df_reindexed.interpolate(method='linear')

# Resample data to 15-minute intervals
df = df_interpolated.resample(delay_timing).agg({
    'open': 'first',
    'high': 'first',
    'low': 'first',
    'close': 'first',
    'volume': 'first'
})

# Create fields required for strategy execution
df['close_change'] = df['close'].diff()
df['return'] = df['close'].pct_change()
df['close_executed'] = 0 # placeholder
df['close_executed_differential'] = 0 # placeholder
df['investment_value'] = 0  # placeholder
df['investment_return_dollar'] = 0 # placeholder
df['investment_return'] = 0 # placeholder

# Function to determine if all returns in the window are consistently positive or negative and
def check_consistency(values):
    if (values > 0 ).all():
        return 1 # All Positive 
    elif (values < 0).all():
        return -1 # All Negative
    else:
        return 0 # Mixed
    
df['consistency'] = df['return'].rolling(window=succession).apply(lambda window: check_consistency(window), raw=False) # Apply the function over a rolling window

# Checks if combined sum of prior returns is over the threshold set above to trigger execution
df['return_rolling_sum'] = df['return'].rolling(window=succession).sum()
df['threshold_met'] = df['return_rolling_sum'].abs() > abs(percentage_threshold)

# Simulating trading
initial_capital = 1000
cash = initial_capital
btc_held = 0
i = -1
t = 0
last_close_executed = None
investment_purchase = None
investment_value = None
investment_return_dollar = None


for index, row in df.iterrows():
    if row['consistency'] > 0 and row['threshold_met'] == True and i == -1: # Buy signal
        btc_held = cash / row['close']
        cash = 0 # Invest all cash
        df.at[index, 'close_executed'] = row['close'] # Update the DataFram directly with the executed price
        last_close_executed = row['close']
        df.at[index, 'investment_value'] = int(investment_value)
        investment_purchase = investment_value
        i *= -1
        t += 1
    elif row['consistency'] < 0 and row['threshold_met'] == True and i == 1: # Sell signal
        cash = btc_held * row['close']
        btc_held = 0 # Sell all holdings
        df.at[index, 'close_executed'] = -row['close'] # Update the DataFram directly with the executed price
        df.at[index, 'close_executed_differential'] = int(row['close']-last_close_executed) # Update the DataFram directly with executed return
        investment_value = (1+row['return'])*investment_value
        df.at[index, 'investment_value'] = int(investment_value)
        investment_return_dollar = investment_value - investment_purchase
        df.at[index, 'investment_return_dollar'] = int(investment_return_dollar)
        i *= -1
        t += 1
    else:
        if t == 0:
            investment_value = cash
            df.at[index,'investment_value'] = int(investment_value)
        elif i == 1: 
            investment_value = (1+row['return'])*investment_value
            df.at[index,'investment_value'] = int(investment_value)
        else:
            df.at[index,'investment_value'] = int(investment_value)

df['investment_return'] = df['investment_value'].pct_change()

print(df)
df.to_csv('C:/Users/kokik/OneDrive/Documents/GitHub/Algorithmic-Bot/stock_df.csv')

# Calculate the final value of the portfolio
final_value = cash if cash > 0 else btc_held * df.iloc[-1]['close']
final_return = (final_value - initial_capital)/initial_capital

default_value = (1+(df.iloc[-1]['close']-df.iloc[0]['close'])/df.iloc[0]['close'])*initial_capital
default_return = (df.iloc[-1]['close']-df.iloc[0]['close'])/df.iloc[0]['close']

span = end - start

print(f"Final portfolio value: ${final_value:.2f} or {round(final_return*100,2)}% return from an initial capital of ${initial_capital} with {t} transactions in a span of {span}")
print(f"Default portfolio value: ${default_value:.2f} or {round(default_return*100,2)}% return from an initial capital of ${initial_capital} with 1 transactions in a span of {span}") # If you were to just buy the stock and hold 

# For purpose of analysis
# Sharpe Ratio = (return of the portfolio - risk free rate) / standard deviation of the portfolio's excess returns (volatility)
#grouped_day = df.groupby(df.index.date).sum()

#print(grouped_day)
#grouped_day.to_csv('test_2.csv')

grouped_month = df.groupby(pd.Grouper(freq='M')).sum()

#print(grouped_month)
#grouped_month.to_csv('test_3')

# Calculate the necessary metrics
mean_return = grouped_month['investment_return'].mean()
print("Mean Return (monthly): ", mean_return)

# Assume a risk-free rate of 4.23% - long-term average of 10 year treasury rate
risk_free_rate = 0.0423
monthly_risk_free_rate = (1+risk_free_rate)**(1/12)-1
print("Risk-Free Rate (monthly): ", monthly_risk_free_rate)

# Calculate the standard deviation of returns (volatility)
std_dev = grouped_month['investment_return'].std()
print("Standard Deviation: ", std_dev) 

# Calculate the Sharpe Ratio (annualized)
sharpe_ratio = (mean_return - monthly_risk_free_rate) / std_dev

print(f"Sharpe Ratio: {round(sharpe_ratio,2)}")