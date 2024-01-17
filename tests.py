import unittest
from datetime import datetime, timedelta
from model import Stock, GBCE

class TestStockCalculator(unittest.TestCase):
    # Set up GBCE, stocks, and trades for tests.
    def setUp(self):
        self.timestamp = datetime.now()
        self.gbce = GBCE()
        self.add_stocks_to_gbce()
        self.add_trades_to_stocks()

    def add_stocks_to_gbce(self):
        self.tea = Stock("TEA", "Common", 0, 0, 100)
        self.pop = Stock("POP", "Common", 8, 0, 100)
        self.ale = Stock("ALE", "Common", 23, 0, 60)
        self.gin = Stock("GIN", "Preferred", 8, 0.02, 100)
        self.joe = Stock("JOE", "Common", 13, 0, 250)
        
        self.gbce.add_stock(self.tea)
        self.gbce.add_stock(self.pop)
        self.gbce.add_stock(self.ale)
        self.gbce.add_stock(self.gin)
        self.gbce.add_stock(self.joe)

    def add_trades_to_stocks(self):
        self.add_trades_to_stock(self.tea, 50, 'buy', 120, 6)
        self.add_trades_to_stock(self.tea, 30, 'sell', 110, 7)
        self.add_trades_to_stock(self.tea, 20, 'buy', 130, 10)

        self.add_trades_to_stock(self.pop, 40, 'buy', 80, 2)
        self.add_trades_to_stock(self.pop, 20, 'sell', 90, 8)
        self.add_trades_to_stock(self.pop, 25, 'buy', 85, 15)

        self.add_trades_to_stock(self.ale, 60, 'buy', 150, 3)
        self.add_trades_to_stock(self.ale, 1150, 'sell', 140, 16)
        self.add_trades_to_stock(self.ale, 25, 'buy', 160, 6)

        self.add_trades_to_stock(self.gin, 25, 'buy', 120, 4)
        self.add_trades_to_stock(self.gin, 344, 'sell', 130, 14)
        self.add_trades_to_stock(self.gin, 10, 'buy', 125, 9)

        self.add_trades_to_stock(self.joe, 30, 'buy', 200, 7)
        self.add_trades_to_stock(self.joe, 18, 'sell', 190, 16)
        self.add_trades_to_stock(self.joe, 22, 'buy', 210, 13)


    def add_trades_to_stock(self, stock, quantity, buy_sell, traded_price, delta_minutes):
        trade_timestamp = self.timestamp - timedelta(minutes=delta_minutes)
        stock.record_trade(trade_timestamp, quantity, buy_sell, traded_price)

    def test_dividend_yield_common(self):
        price = 150
        
        # Dividend yield for Common stock with zero last dividend
        expected_yield_tea = 0
        dividend_yield_tea = self.tea.calculate_dividend_yield(price)
        self.assertEqual(dividend_yield_tea, expected_yield_tea)

        # Dividend yield for Common stock with positive last dividend
        expected_yield_pop = self.pop.last_dividend / price
        dividend_yield_pop = self.pop.calculate_dividend_yield(price)
        self.assertEqual(dividend_yield_pop, expected_yield_pop)

        # Dividend yield for prize zero (division by zero)
        price_zero = 0
        with self.assertRaises(ValueError) as context:
            self.ale.calculate_dividend_yield(price_zero)
    
        self.assertEqual(str(context.exception), "Price must be a positive number")

    def test_dividend_yield_preferred(self):
        price = 150
        # Dividend yield for Preferred stock
        dividend_yield_gin = self.gin.calculate_dividend_yield(price)
        expected_yield_gin = (self.gin.fixed_dividend * self.gin.par_value) / price
        self.assertEqual(dividend_yield_gin, expected_yield_gin)

        # Dividend yield for price zero (division by zero)
        price_zero = 0        
        with self.assertRaises(ValueError) as context:
            self.gin.calculate_dividend_yield(price_zero)
    
        self.assertEqual(str(context.exception), "Price must be a positive number")

            
    def test_pe_ratio(self):
        price = 150
        # PE ratio for zero last dividend  (diving zero)
        with self.assertRaises(ValueError) as context:
            self.tea.calculate_pe_ratio(price)
        self.assertEqual(str(context.exception), "Cannot calculate P/E ratio when last dividend is zero") # Expecting error for dividing with zero last dividend

        # PE ratio for a stock
        pe_ratio_pop = self.pop.calculate_pe_ratio(price)
        expected_ratio_pop = price / self.pop.last_dividend # The last divident will have been updated as the the calculate_dividend_yield has been called.
        self.assertEqual(pe_ratio_pop, expected_ratio_pop)
        # PE ratio for a stock
        pe_ratio_ale = self.ale.calculate_pe_ratio(price)
        expected_ratio_ale = price / self.ale.last_dividend
        self.assertEqual(pe_ratio_ale, expected_ratio_ale)
        
        # PE ratio for price zero
        price_zero = 0
        with self.assertRaises(ValueError) as context:
            self.ale.calculate_pe_ratio(price_zero)
        self.assertEqual(str(context.exception), "Price must be a positive number") 

        # PE ratio for negative price
        price_negative = -50
        with self.assertRaises(ValueError) as context:
            self.ale.calculate_pe_ratio(price_negative)
        self.assertEqual(str(context.exception), "Price must be a positive number") 

    def test_volume_weighted_stock_price(self):
        # Calculating volume-weighted stock price for APPL stock
        self.appl = Stock("AAPL", "Common", 34, 0, 100)
        vwsp_appl = self.appl.calculate_volume_weighted_stock_price()
        self.assertEqual(vwsp_appl, 0)  # No trades, expecting 0
        
        #Adding trades with timestamps <15 minutes to APPL stock. Recalculating
        self.appl.record_trade(self.timestamp - timedelta(minutes=2), 50, 'buy', 120)
        self.appl.record_trade(self.timestamp - timedelta(minutes=1), 30, 'sell', 110)
        self.appl.record_trade(self.timestamp, 20, 'buy', 130)

        expected_vwsp_appl = (50 * 120 + 30 * 110 + 20 * 130) / (50 + 30 + 20)
        vwsp_appl_calculated = self.appl.calculate_volume_weighted_stock_price()
        self.assertEqual(vwsp_appl_calculated, expected_vwsp_appl)
        
        # Trade on stock after 15 minutes will not change the calulation of Volume Weighted Stock Price 
        self.appl.record_trade(self.timestamp - timedelta(minutes=15), 20, 'buy', 130)
        last_trade = self.appl.trades[0][1]
        vwsp_appl_calculated = self.appl.calculate_volume_weighted_stock_price()
        self.assertEqual(vwsp_appl_calculated, expected_vwsp_appl)
 

    def test_record_trade(self):
        quantity = 50
        traded_price = 120
        timestamp_5min_ago = self.timestamp - timedelta(minutes=5)
        timestamp_now =  self.timestamp

        # Record a valid sell trade for Common stock
        self.tea.record_trade(timestamp_5min_ago, quantity, 'sell', traded_price)
        last_trade = self.tea.trades[0][1]  # Get the last trade object (root of the trades priority queue)
        self.assertEqual(last_trade.timestamp, timestamp_5min_ago)
        self.assertEqual(last_trade.quantity, quantity)
        self.assertEqual(last_trade.buy_sell, 'sell')
        self.assertEqual(last_trade.price, traded_price)
        
        # Record a valid buy trade for Common stock for 0 price (to cover case of Bankruptcy)
        zero_price = 0
        self.tea.record_trade(timestamp_now, quantity, 'buy', zero_price)
        last_trade = self.tea.trades[0][1]  # Get the last trade object (root of the trades priority queue)
        self.assertEqual(last_trade.timestamp, timestamp_now)
        self.assertEqual(last_trade.quantity, quantity)
        self.assertEqual(last_trade.buy_sell, 'buy')
        self.assertEqual(last_trade.price, zero_price)
    
        # Adding trade with invalid buy/sell indicator
        with self.assertRaises(ValueError) as context:
            self.tea.record_trade(timestamp_now, 20, 'invalid', 130)
        self.assertEqual(str(context.exception), "Indicator must be 'buy' or 'sell'")

        # Adding trade with zero quantity
        with self.assertRaises(ValueError) as context:
            self.tea.record_trade(timestamp_now, 0, 'buy', 125)
        self.assertEqual(str(context.exception), "Quantity must be a positive integer")
        
        # Adding trade with negative quantity
        with self.assertRaises(ValueError) as context:
            self.tea.record_trade(timestamp_now, -10, 'sell', 115)
        self.assertEqual(str(context.exception), "Quantity must be a positive integer")

        # Adding trade with negative traded price
        with self.assertRaises(ValueError) as context:
            self.tea.record_trade(timestamp_now, 15, 'buy', -125)
        self.assertEqual(str(context.exception), "Price must be a positive number")

        
    def test_calculate_all_share_index(self):
        # GBCE index multiple stocks with varying prices
        all_share_index_multiple_stocks = self.gbce.calculate_all_share_index()
        expected_index = (
            self.tea.calculate_volume_weighted_stock_price() *
            self.pop.calculate_volume_weighted_stock_price() *
            self.ale.calculate_volume_weighted_stock_price() *
            self.gin.calculate_volume_weighted_stock_price() *
            self.joe.calculate_volume_weighted_stock_price()) ** (1/5)
        self.assertEqual(all_share_index_multiple_stocks, expected_index)

        self.gbce.stocks =[]
        # GBCE index no stocks
        all_share_index_no_stocks = self.gbce.calculate_all_share_index()
        self.assertEqual(all_share_index_no_stocks, 0)  # No stocks, expecting 0
        
        self.gbce.add_stock(self.tea)
        
        # GBCE index one stock
        all_share_index_one_stock = self.gbce.calculate_all_share_index()
        self.assertEqual(all_share_index_one_stock, self.tea.calculate_volume_weighted_stock_price())

        # GBCE index 3 stocks have no trades
        self.tea.trades = []  # Remove trades for stocks
        self.pop.trades = []
        self.ale.trades = []
        self.joe.trades = []
        self.gbce.add_stock(self.pop)
        self.gbce.add_stock(self.ale)
        self.gbce.add_stock(self.joe)

        partial_index = self.gbce.calculate_all_share_index()
        self.assertEqual(partial_index, 0)  # Expecting 0 due to missing trade data


if __name__ == '__main__':
    unittest.main()
