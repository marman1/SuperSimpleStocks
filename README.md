# SuperSimpleStocks

This Python module implements a simple stock market simulation based on requirements of the assignment. It defines three classes: Stock, Trade, and GBCE.

###### Stock

The Stock class represents a stock in the stock market. It has the following **attributes**:
- *symbol*: The ticker symbol of the stock
- *stock_type*: The type of stock ("Common" or "Preferred") 
- *last_dividend*: The last dividend paid by the stock (>= 0). It will be updated when calculate_dividend_yield is called.
- *fixed_dividend*: The fixed dividend for a Preferred stock (0 <= fixed_divident >= 1)
- *par_value*: The par value of a Preferred stock ((> 0))
- *trades*: A priority queue of Trade objects for the stock. The priority queue is implemented using - headq ((priority : int of timestamp, value : the Trade object)). The reason for this choice of data structure was made for better performance in case of a great number of trades.

The Stock class has the following **methods**:
- *calculate_dividend_yield(price)*: Calculates the dividend yield of the stock. And updates the last_divident value of the stock.
- *calculate_pe_ratio(price)*: Calculates the P/E ratio of the stock.
- *record_trade(timestamp, quantity, buy_sell, traded_price)*: Records a trade for the stock.

###### Trade

The Trade class represents a trade in the stock market. It has the following **attributes**:

- *timestamp*: The timestamp of the trade 
- *quantity*: The quantity of shares traded (> 0, as there is no meaning of a trade if there is no quantity)
- *buy_sell*: Whether the trade is a buy or a sell ("buy" or "sell") 
- *price*: The price per share of the trade (>= 0, the case of accepting 0 is the case of bankruptcy..)

###### GBCE

The GBCE class represents the Global Baltic Composite Exchange (GBCE). It has the following **attributes**:
- *stocks*: A list of Stock objects in the GBCE

The GBCE class has the following **methods**:
- *add_stock(stock)*: Adds a stock to the GBCE.
- *calculate_all_share_index()*: Calculates the All-Share Index of the GBCE.

###### Usage 
To use this module, first a GBCE object can be created and some stocks can be added to it. Then, trades can be recorded for the stocks and the GBCE All-Share Index can be calculate.

Here is an example of how to use the module:

    # Create a GBCE object
    gbce = GBCE()

    # Create some stocks
    pop = Stock("POP", "Common", 8, 0, 100)
    gin = Stock("GIN", "Preferred", 8, 0.02, 100)

    # Add the stocks to the GBCE
    gbce.add_stock(tea)
    gbce.add_stock(pop)

    # Record some trades
    gbce.pop.record_trade(datetime.now(), 40, 'buy', 80)
    gbce.pop.record_trade(datetime.now(), 20, 'sell', 90)
    gbce.pop.record_trade(datetime.now(), 25, 'buy', 85)
