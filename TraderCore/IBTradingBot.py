from ibapi.contract import Contract
from ibapi.wrapper import BarData
from threading import Thread
import time

from TradingCosts import TradingCosts
import HelperFunctions as hf

class IBTradingBot(object):
   ib_api = None

   # Trade Bookkeeping
   profit = 0
   total_fees = 0
   total_slipage = 0
   day_profit = 0
   num_trades = 0
   short_trades = 0
   long_trades = 0
   max_drawdown = 0
   day_profit_list = []
   num_trading_periods = 0
   stop_trades = 0
   id_number = 0

   # state
   holding = False
   position_type = None
   held_position_price = 0
   held_quantity = 0

   # Shares
   short_quantity = 1
   long_quantity = 1

   def __init__(self, cost: TradingCosts, capital, bar_storage_size=120, simulation=True, printing=False):
      if not simulation:
         # self.ib_api = IBApi(self)
         # self.ib_api.connect("192.168.50.243", 7497, 2)
         ib_process = Thread(target=self.run_loop, daemon=True)
         ib_process.start()
         time.sleep(1)

      # Bar storage
      self.bar_storage_size = bar_storage_size
      self.bar_list = []
      for _ in range(self.bar_storage_size):
         self.bar_list.append(hf.make_bar(*[0]*8))

      self.trading_costs = cost
      self.simulation = simulation
      self.printing = False
      self.capital = capital

      # Contracts
      self.underlying_contract = Contract()
      self.underlying_contract.symbol = "QQQ"
      self.underlying_contract.secType = "STK"
      self.underlying_contract.exchange = "SMART"
      self.underlying_contract.currency = "USD"

      self.short_contract = Contract()
      self.short_contract.symbol = "SQQQ"
      self.short_contract.secType = "STK"
      self.short_contract.exchange = "SMART"
      self.short_contract.currency = "USD"

      self.long_contract = Contract()
      self.long_contract.symbol = "TQQQ"
      self.long_contract.secType = "STK"
      self.long_contract.exchange = "SMART"
      self.long_contract.currency = "USD"

      if simulation:
         self.trading_enabled = True
      else:
         self.trading_enabled = False

      self.buy_enabled = True

   def disable_buying(self):
      self.buy_enabled = False

   def run_loop(self):
      #self.ib_api.run()
      #TODO
      pass

   def on_bar_update(self, underlying_bar: BarData, short_bar: BarData, long_bar: BarData):
      print(underlying_bar.close)

   def update_bar_list(self, new_bar: BarData):
      self.bar_list.append(new_bar)
      self.bar_list.pop(0)

   def open_long_position(self, price: float):
      if not self.holding and self.buy_enabled:
         if self.printing:
            print("Attempting to open long position at %s price" % price)
         if self.simulation:
            self.simulated_position_open("long", price, self.long_quantity)
         else:
            pass #TODO production trading
         return True
      else:
         return False

   def open_short_position(self, price: float):
      if not self.holding and self.buy_enabled:
         if self.printing:
            print("Attempting to open short position at %s price" % price)
         if self.simulation:
            self.simulated_position_open("short", price, self.short_quantity)
         else:
            pass #TODO production trading
         return True
      else:
         return False

   def close_short_position(self, price: float):
      if self.holding and self.position_type == "short":
         if self.printing:
            print("Attempting to close short position at %s price" % price)
         if self.simulation:
            self.simulated_position_close(price)
            self.short_trades += 1
         else:
            pass #TODO production trading
         return True
      else:
         return False

   def close_long_position(self, price: float):
      if self.holding and self.position_type == "long":
         if self.printing:
            print("Attempting to close long position at %s price" % price)
         if self.simulation:
            self.simulated_position_close(price)
            self.long_trades += 1
         else:
            pass #TODO production trading
         return True
      else:
         return False

   def simulated_position_open(self, pos_type: str, price: float, quantity: int):
      self.position_type = pos_type
      self.holding = True
      self.held_position_price = price
      self.held_quantity = quantity
      fees, slipage = self.trading_costs.compute_cost(quantity, price, True)
      self.total_fees += fees
      self.total_slipage += slipage
      self.day_profit -= (fees + slipage)

   def simulated_position_close(self, price: float):
      fees, slipage = self.trading_costs.compute_cost(self.held_quantity, price, False)
      self.total_fees += fees
      self.total_slipage += slipage

      self.day_profit += (price - self.held_position_price) * self.held_quantity - fees - slipage

      self.held_position_price = 0
      self.held_quantity = 0
      self.position_type = None
      self.holding = False
      self.num_trades += 1

   def start_new_trading_period(self):
      self.day_profit_list.append(self.day_profit)
      self.profit += self.day_profit
      self.day_profit = 0
      self.num_trading_periods += 1
      self.buy_enabled = True
      if self.profit < self.max_drawdown:
         self.max_drawdown = self.profit

   def compute_share_quantities(self, short_price, long_price):
      self.long_quantity = int(self.capital / long_price)
      self.short_quantity = int(self.capital / short_price)


   def close_all_positions(self, short_price, long_price):
      self.close_short_position(short_price)
      self.close_long_position(long_price)

   def print_stats(self):
      profit_per_day = self.profit / self.num_trading_periods if self.num_trading_periods != 0 else 0
      print("Capital: %s, Profit: %s, Trades: (%s, %s, %s), Day Avg: %s, Drawdown: %s, Stops: %s, Costs: %s" % (self.capital, self.profit, self.num_trades, self.short_trades, \
                                                                                                                self.long_trades, profit_per_day, self.max_drawdown, self.stop_trades, \
                                                                                                                self.total_slipage + self.total_fees))
