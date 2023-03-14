import logging

from ibapi.wrapper import BarData

from TraderCore.TradingCosts import TradingCosts, ibkr_trading_costs
from pathlib import Path
import os
import json

class TraderBase(object):
   # Stats
   profit = 0
   drawdown = 0
   num_trades = 0
   short_trades = 0
   long_trades = 0
   stop_trades = 0
   day_profit = 0

   # Trading costs
   total_costs = 0
   slipage = 0
   fees = 0

   # Trade bookkeeping
   holding = None
   num_pending = 0
   num_held = 0
   average_price = 0
   open_or_close = None

   # Trade logic
   trading_enabled = False
   data_length = 1

   # Helper
   ticker = None


   def __init__(self, cost: TradingCosts=ibkr_trading_costs, simulation: bool=True, log_level: int=logging.WARNING, log_file_name: str="", name: str="none_bot", leverage: float=1.0, save_dir="Save/") -> None:
      if log_file_name != "":
         logging.basicConfig(filename=log_file_name, filemode='a', encoding='utf-8', level=log_level)
      else:
         logging.basicConfig(level=log_level)
      self.trading_costs = cost
      self.simulation = simulation
      self.name = name
      self.day_profit_list = []
      self.leverage = leverage
      self.save_name = save_dir + self.name + ".json"

      if not self.simulation:
         # Create/open save file
         if not Path.exists(path):
            os.makedirs(path)
         path = Path(self.save_name)
         if not path.is_file():
            print("save does not exist, creating: " + self.save_name)
            with open(self.save_name, 'w') as sv:
               sv.write("{}")

      logging.info("Created " + self.name)
      logging.info(self.trading_costs)

   def process(self, bar):
      return self.open_or_close, self.holding, self.num_pending

   def reset(self, position_close: str=False):
      pass

   def open_position(self, price: float, quantity: int, order_t: str):
      if self.holding is None and self.trading_enabled and self.num_pending == 0:
         logging.info(f"Opening {order_t} position @ {price}")
         self.holding = order_t
         self.num_pending = quantity
         self.open_or_close = "open"
         self.average_price = price
         if self.simulation:
            self.simulate_costs(quantity, price, True)
            self.confirm_open(price, quantity)

   def close_position(self, price: float, quantity: int):
      if self.holding is not None and self.trading_enabled and self.num_pending == 0:
         logging.info(f"Closing {self.holding} position @ {price}")
         self.num_pending = quantity
         self.open_or_close = "close"
         if self.simulation:
            self.simulate_costs(quantity, price, False)
            self.confirm_close(price, quantity)
   
   def simulate_costs(self, quantity, price, buy):
      fees, slipage = self.trading_costs.compute_cost(quantity, price, buy)
      self.fees += fees
      self.slipage += slipage
      self.total_costs += fees + slipage
      self.profit -= (fees + slipage)
      self.drawdown = min(self.drawdown, self.profit)

   def confirm_open(self, price: float, quantity: int):
      #TODO partial order fill?
      self.open_or_close = None
      self.num_pending = 0
      self.num_held = quantity
      self.average_price = price

   def confirm_close(self, price: float, quantity: int):
      #TODO partial order fill?
      self.num_trades += 1
      if self.holding == 'long':
         self.profit += (price - self.average_price) * quantity * self.leverage
         self.long_trades += 1
      elif self.holding == 'short':
         self.profit += (self.average_price - price) * quantity * self.leverage
         self.short_trades += 1
      self.num_pending = 0
      self.num_held = 0
      self.average_price = 0
      self.holding = None
      self.open_or_close = None

   def save_value(self, key, value):
      if self.simulation:
         return
      data = None
      save = open(self.save_name, "r")
      data = json.load(save)
      save.close()

      data[key] = value

      save = open(self.save_name, "w")
      json.dump(data, save)
      save.close()

   @staticmethod
   def compute_share_quantity(price, capital):
      return int(capital / price)

   def __eq__(self, other):
      return self.profit == other.profit

   def __lt__(self, other):
      return self.profit < other.profit

   def __gt__(self, other):
      return self.profit > other.profit

   def __le__(self, other):
      return self.profit <= other.profit

   def __ge__(self, other):
      return self.profit >= other.profit
   
   def get_stats(self):
      return "%s: Profit: %s, Ticker: %s, Trades: (%s, %s, %s), Drawdown: %s, Stops: %s, Costs: %s" % (self.name, self.profit, self.ticker, self.num_trades, self.short_trades, \
                                                                                                self.long_trades, self.drawdown, self.stop_trades, self.total_costs)

   def print_stats(self):
      info_str = self.get_stats()

      print(info_str)
      logging.info(info_str)

   def __str__(self):
      return "TraderBase"
