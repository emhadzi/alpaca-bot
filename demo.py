import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
# den xero poio ao ta dyo einai to sosto (.historical ?)
from alpaca.data import StockHistoricalDataClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime
from alpaca.data.live import StockDataStream

load_dotenv()

# keys required
# manoli zhta api gia stocks
stock_client = StockHistoricalDataClient(api_key=os.getenv("APCA_API_KEY"), 
                                         secret_key=os.getenv("APCA_API_SECRET"))

# GIA NA PARO THN TELEUTAI TIMH TWN METOXWN
# multi symbol request - single symbol is similar
multisymbol_request_params = StockLatestQuoteRequest(symbol_or_symbols=["SPY", "GLD", "TLT"])

latest_multisymbol_quotes = stock_client.get_stock_latest_quote(multisymbol_request_params)

# example
spy_latest_ask_price = latest_multisymbol_quotes["SPY"].ask_price

# GIA COMPLETE HISTORICAL DATA
# example for SPY
request_params = StockBarsRequest(
                        symbol_or_symbols=["SPY"],
                        timeframe=TimeFrame.Day,    # syxnothta dedomenwn
                        start=datetime(2026, 1, 1), # start date
                        end=datetime(2026, 3, 1)    # end date
)

# gia na paro exact time dld mexri thn prohgoumeni mera:
# ???

bars = stock_client.get_stock_bars(request_params)

# convert to dataframe
bars.df

# access bars as list - important to note that you must access by symbol key
# even for a single symbol request - models are agnostic to number of symbols
print(bars["SPY"])

# REAL TIME DATA

stock_stream = StockDataStream(
    api_key=os.getenv("APCA_API_KEY"),
    secret_key=os.getenv("APCA_API_SECRET")
)





trading_client = TradingClient(
    api_key=os.getenv("APCA_API_KEY"),
    secret_key=os.getenv("APCA_API_SECRET"),
    paper=True
)

# preparing orders
market_order_data = MarketOrderRequest(
                    symbol="SPY",
                    qty=0.5,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY
                    )

# Market order
# market_order = trading_client.submit_order(
#                order_data=market_order_data
#               )


# # preparing limit order
# limit_order_data = LimitOrderRequest(
#                     symbol="SPY",
#                     limit_price=771.00,
#                     qty=0.5,
#                     side=OrderSide.SELL,
#                     time_in_force=TimeInForce.DAY
#                    )

# # Limit order
# limit_order = trading_client.submit_order(
#                 order_data=limit_order_data
#               )
