import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

load_dotenv()

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
market_order = trading_client.submit_order(
                order_data=market_order_data
               )


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