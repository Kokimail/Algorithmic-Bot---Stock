from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta

# setting API properties
API_KEY = 'PK2I5CCKUGXSDUMF5729'
API_SECRET = 'R2ETLhRBNHgsFWeI9VfLhT0cijt6hBi0giUuM0jx'
BASE_URL = 'https://paper-api.alpaca.markets/v2'

trading_client = TradingClient(API_KEY,API_SECRET, paper=True)
data_client = StockHistoricalDataClient(API_KEY, API_SECRET)

# requesting account data
print(trading_client.get_account().account_number)
print(trading_client.get_account().cash) 


# requesting current ask price
multisymbol_request_params = StockLatestQuoteRequest(symbol_or_symbols=["SPY","GLD","TLT","AMZN"])
latest_muyltisymbol_quotes = data_client.get_stock_latest_quote(multisymbol_request_params)
gld_latest_ask_price = latest_muyltisymbol_quotes["AMZN"].ask_price
print(gld_latest_ask_price)

# requesting historical bar data
request_params = StockBarsRequest(
    symbol_or_symbols = ["AMZN"],
    timeframe = TimeFrame.Day,
    start = datetime(2022,7,1),
    end = datetime(2022,9,1)
)

bars = data_client.get_stock_bars(request_params)

bars.df

print(bars.df)