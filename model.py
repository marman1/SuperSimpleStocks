from datetime import datetime, timedelta
from math import pow
import heapq
import copy


def to_int(func):
    def wrapper(date_time):
        # Check if the input is a datetime object
        if not isinstance(date_time, datetime):
            raise TypeError('date_time must be a datetime object')      
        # Convert the datetime object to an integer representing the timestamp
        return func(int(date_time.timestamp()))
    return wrapper

@to_int
def get_date_as_int(date_time):
    # Return the integer representation of the timestamp
    return date_time


class Trade:
    # Represents a trade in a stock.
    # Attributes:
    #     timestamp: The timestamp of the trade.
    #     quantity: The quantity of shares traded.
    #     buy_sell: Whether the trade is a buy ('buy') or a sell ('sell').
    #     price: The price per share of the trade.

    def __init__(self, timestamp, quantity, buy_sell, price):
        # Check if the timestamp is a datetime object
        if not isinstance(timestamp, datetime):
            raise ValueError("Timestamp must be a datetime object")
        # Check if the quantity is a positive integer
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer")
        # Check if the buy_sell value is 'buy' or 'sell'
        if buy_sell not in {'buy', 'sell'}:
            raise ValueError("Indicator must be 'buy' or 'sell'")
        # Check if the price is a positive number
        if not isinstance(price, (int, float)) or price <= 0:
            raise ValueError("Price must be a positive number")
        
        self.timestamp = timestamp
        self.quantity = quantity
        self.buy_sell = buy_sell
        self.price = price
        
        
class Stock:
    # Represents a stock in a stock exchange.
    # Attributes:
    #     symbol: The ticker symbol of the stock.
    #     stock_type: The type of stock ('Common' or 'Preferred').
    #     last_dividend: The last dividend paid by the stock.
    #     fixed_dividend: The fixed dividend for Preferred stock (only applicable if stock_type is 'Preferred').
    #     par_value: The par value of the stock (only applicable if stock_type is 'Preferred').
    #     trades: A priority queue of Trade objects for the stock. 
    #             The priority queue is implemented using headq ((priority : int of timestamp, value : the Trade object))
        
    def __init__(self, symbol, stock_type, last_dividend, fixed_dividend, par_value):
        # Validate the stock_type
        if stock_type not in {'Common', 'Preferred'}:
            raise ValueError("Stock type must be 'Common' or 'Preferred'")
        # Validate the last_dividend
        if not isinstance(last_dividend, (int, float)) or last_dividend < 0:
            raise ValueError("Last dividend must be a non-negative number")
        # Validate the fixed_dividend (if applicable)
        if stock_type == 'Preferred' and (not isinstance(fixed_dividend, (int, float)) or fixed_dividend < 0 or fixed_dividend > 1):
            raise ValueError("Fixed dividend for Preferred stock must be a number between 0 and 1")
        # Validate the par_value
        if not isinstance(par_value, (int, float)) or par_value <= 0:
            raise ValueError("Par value must be a positive number")
        
        self.symbol = symbol
        self.type = stock_type
        self.last_dividend = last_dividend
        self.fixed_dividend = fixed_dividend
        self.par_value = par_value
        self.trades = [] # priority queue (priority : int of timestamp, value : the Trade object)

    def calculate_dividend_yield(self, price):
        if price <= 0:
            raise ValueError("Price must be a positive number")
        
        # Calculate the dividend yield based on the stock type
        divident = 0
        if self.type == "Common":
            divident = self.last_dividend / price
        elif self.type == "Preferred":
            divident = (self.fixed_dividend * self.par_value) / price
        
        # Update the stock's last_dividend
        self.last_dividend = divident
        return divident

    def calculate_pe_ratio(self, price):
        # Validate the price
        if price <= 0:
            raise ValueError("Price must be a positive number")
        
        divident = self.calculate_dividend_yield(price)
        # Validate the last_dividend
        if self.last_dividend == 0:
            raise ValueError("Cannot calculate P/E ratio when last dividend is zero")
        
        return price / divident

    def record_trade(self, timestamp, quantity, buy_sell, traded_price):
        # New trade
        trade = Trade(timestamp, quantity, buy_sell, traded_price)
        
        # Convert provided timestamp to int and reverse to negative 
        # to serve as a priotity in the trades priority queue.
        # In this way, the latest trade will be in the root of the heap.
        int_timestamp = - get_date_as_int(timestamp)

        heapq.heappush(self.trades, (int_timestamp, trade))
        

    def calculate_volume_weighted_stock_price(self):
        now = datetime.now()
        fifteen_minutes_ago = now - timedelta(minutes=15)
        
        # Initialize relevant_trades and original_trades_copy in order to preserve the trades object
        relevant_trades = []
        original_trades_copy = copy.deepcopy(self.trades)
        
        while original_trades_copy:
            timestamp, trade = heapq.heappop(original_trades_copy)
            
            if trade.timestamp >= fifteen_minutes_ago:
                # If the timestamp is within the 15-minute window, append the trade to relevant_trades
                relevant_trades.append(trade)
            else:
                # If the timestamp is outside the 15-minute window, break out of the loop,
                # as all other trades are older than 15 minutes
                break
            
        # If no trades exist for the last 15 minutes 
        if not relevant_trades:
            return 0
        
         # Calculate the volume-weighted stock price
        total_price_quantity = sum(trade.price * trade.quantity for trade in relevant_trades)
        total_quantity = sum(trade.quantity for trade in relevant_trades)

        return total_price_quantity / total_quantity if total_quantity != 0 else None



class GBCE:
    # Represents the Global Baltic Composite Exchange (GBCE).
    # Attributes:
    #     stocks: A list of Stock objects.
    
    def __init__(self):
        self.stocks = []

    def add_stock(self, stock):
        self.stocks.append(stock)

    #Calculates the All-Share Index of the GBCE using geometric mean
    def calculate_all_share_index(self):
        prices = [stock.calculate_volume_weighted_stock_price() for stock in self.stocks if stock.calculate_volume_weighted_stock_price() != 0]

        return GBCE.calculate_geometric_mean(prices)

    @staticmethod
    def calculate_geometric_mean(prices):
        product = 1
        for price in prices:
            product *= price
        return pow(product, 1/len(prices)) if len(prices) > 0 else 0
