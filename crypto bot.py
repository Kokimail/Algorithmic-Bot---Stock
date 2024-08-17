from alpaca.trading.client import TradingClient
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame

# setting API properties
API_KEY = 'PK2I5CCKUGXSDUMF5729'
API_SECRET = 'R2ETLhRBNHgsFWeI9VfLhT0cijt6hBi0giUuM0jx'
BASE_URL = 'https://paper-api.alpaca.markets/v2'

trading_client = TradingClient(API_KEY,API_SECRET, paper=True)

