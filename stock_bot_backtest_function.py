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
import warnings

'''
Fetch current directory
'''
current_directory = os.path.dirname(os.path.abspath(__file__)) # for the purpose of setting file_path

'''
Fetch historical data
'''
# setting API properties
API_KEY = 'PK2I5CCKUGXSDUMF5729'
API_SECRET = 'R2ETLhRBNHgsFWeI9VfLhT0cijt6hBi0giUuM0jx'
BASE_URL = 'https://paper-api.alpaca.markets/v2'

# initialize the trading and data clients
trading_client = TradingClient(API_KEY,API_SECRET, paper=True)
data_client = StockHistoricalDataClient(API_KEY,API_SECRET)


'''
Set data fetch function
'''
def get_stock_data (stock, start_datetime, end_datetime):
    test_bar_request = StockBarsRequest(
        symbol_or_symbols = [stock],
        timeframe = TimeFrame.Minute,
        start = start_datetime,
        end = end_datetime
    )

    test_bars = data_client.get_stock_bars(test_bar_request)

    # Convert data to DataFrame
    df = pd.DataFrame(test_bars.df)
    print(df)
    print(df.index.get_level_values('symbol')[0])
    # Ignore FutureWarnings
    warnings.simplefilter(action='ignore', category=FutureWarning)

    return df


'''
Set backtest function
'''

def momentum_trading_backtest(delay_timing, succession, percentage_threshold, df):
    # Generate a complete datetime index from start to finish at one-minute intervals
    start = df.index.get_level_values('timestamp').min()
    end = df.index.get_level_values('timestamp').max()
    complete_index = pd.date_range(start=start, end=end, freq = 'T') # 'T' for minute frequency
    df['symbol'] = df.index.get_level_values('symbol')

    # Reindex btc_df using complete time index
    stock_df = df.loc[stock]
    df_reindexed = stock_df.reindex(complete_index)

    # Interpolate missing values linearly
    df_interpolated = df_reindexed.interpolate(method='linear')

    # Resample data to 15-minute intervals
    df = df_interpolated.resample(delay_timing).agg({
        'symbol': 'first',
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
    df['sec_fee'] = 0 # placeholder
    df['finra_fee'] = 0 # placeholder
    df['total_fees'] = 0 # placeholder

    # Function to determine if all returns in the window are consistently positive or negative
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
    sec_fee = None
    finra_fee = None
    total_fees = None


    for index, row in df.iterrows():
        if row['consistency'] > 0 and row['threshold_met'] == True and i == -1: # Buy signal
            df.at[index, 'close_executed'] = row['close'] # Update the DataFram directly with the executed price
            last_close_executed = row['close']
            df.at[index, 'investment_value'] = int(investment_value)
            investment_purchase = investment_value
            btc_held = cash / row['close']
            cash = 0 # Invest all cash
            i *= -1
            t += 1
        elif row['consistency'] < 0 and row['threshold_met'] == True and i == 1: # Sell signal
            df.at[index, 'close_executed'] = -row['close'] # Update the DataFram directly with the executed price
            df.at[index, 'close_executed_differential'] = int(row['close']-last_close_executed) # Update the DataFram directly with executed return
            investment_value = (1+row['return'])*investment_value # would be investment value without the fees
            investment_return_dollar = investment_value - investment_purchase # would be return dollar value without the fees
            sec_fee = 0.0000278*investment_value # 27.80 per $1,000,000 of principal (sells only) (https://files.alpaca.markets/disclosures/library/BrokerAPIExhibitB.pdf)
            df.at[index, 'sec_fee'] = sec_fee
            finra_fee = 0.000166*btc_held # 0.000166 per share (sells only) (https://files.alpaca.markets/disclosures/library/BrokerAPIExhibitB.pdf)
            df.at[index, 'finra_fee'] = finra_fee
            total_fees = sec_fee + finra_fee # calculate the total fees
            df.at[index, 'total_fees'] = total_fees
            investment_value = investment_value - total_fees # incorporating fees to investment value
            df.at[index, 'investment_value'] = investment_value
            investment_return_dollar = investment_return_dollar - total_fees # incorporating fees to return dollar value
            df.at[index, 'investment_return_dollar'] = investment_return_dollar
            cash = btc_held * row['close'] - total_fees # cash value minus the fees
            btc_held = 0 # Sell all holdings
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

    filename_stock = df['symbol'].iloc[0]
    filename = f"{filename_stock}_{delay_timing}_{succession}_{percentage_threshold}.csv" # file naming convention will be 'stock_delay timing_succession_percentage threshold'
    file_path = os.path.join(current_directory,'Data dump', filename)
    df.to_csv(file_path)

    # Calculate the final value of the portfolio
    final_value = cash if cash > 0 else btc_held * df.iloc[-1]['close']
    final_return = (final_value - initial_capital)/initial_capital

    default_value = (1+(df.iloc[-1]['close']-df.iloc[0]['close'])/df.iloc[0]['close'])*initial_capital
    default_return = (df.iloc[-1]['close']-df.iloc[0]['close'])/df.iloc[0]['close']

    # For purpose of analysis
    # Sharpe Ratio = (return of the portfolio - risk free rate) / standard deviation of the portfolio's excess returns (volatility)

    grouped_month = df.groupby(pd.Grouper(freq='M')).sum()

    # Calculate the necessary metrics
    mean_return = grouped_month['investment_return'].mean()

    # Assume a risk-free rate of 4.23% - long-term average of 10 year treasury rate
    risk_free_rate = 0.0423
    monthly_risk_free_rate = (1+risk_free_rate)**(1/12)-1

    # Calculate the standard deviation of returns (volatility)
    std_dev = grouped_month['investment_return'].std()

    # Calculate the Sharpe Ratio (annualized)
    sharpe_ratio = (mean_return - monthly_risk_free_rate) / std_dev

    # Function to return the following
    #return final_value, final_return, default_value, default_return, sharpe_ratio
    return final_value


'''
Run backtest over a range of parameters
'''

# Set variables to fetch historical data
stocks = ["NVDA", "TSLA"] # rest of the list: "MSFT", "AAPL", "AMD", "AMZN", "SMCI", "META", "MSTR", "AVGO", "SPY"
start_datetime = datetime(2021,1,1)
end_datetime = datetime(2021,1,15)

stock_data = {stock: get_stock_data(stock, start_datetime, end_datetime) for stock in stocks}

# Set variables to configure backtest
delay_timings = ['1T', '5T', '15T', '30T', '1H']
successions = [1, 2, 3]
percentage_thresholds = [0.000, 0.001, 0.005, 0.01]
results = [] # Leave this blank

# Run backtest
for stock in stocks:
    df = stock_data[stock]
    for delay_timing in delay_timings:
        for succession in successions:
            for percentage_threshold in percentage_thresholds:
                roi = momentum_trading_backtest(delay_timing, succession, percentage_threshold, df)
                results.append((stock, delay_timing, succession, percentage_threshold, roi))

results_df = pd.DataFrame(results, columns = ['stock', 'delay_timing', 'succession', 'percentage_threshold', 'roi'])
print(results_df)
file_path = os.path.join(current_directory,"results_df.csv")
results_df.to_csv(file_path)

