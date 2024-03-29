from TraderCore.TradingCosts import TradingCosts, ibkr_trading_costs

import os
from pathlib import Path
import logging
import json
from threading import Lock
logger = logging.getLogger(__name__)

class LiveTraderBase(object):
   # Stats
   profit = 0
   drawdown = 0
   num_trades = 0
   short_trades = 0
   long_trades = 0
   stop_trades = 0
   win_trades = 0
   win_percent = 0.0

   # Trading
   num_held = 0
   num_pending = 0
   average_price = 0
   capital = 0
   trading_enabled = False
   ticker = None
   data_length = 0
   purge_count = 0

   # Trading costs
   total_costs = 0
   slipage = 0
   fees = 0

   # Threading support
   watchdog_pet = False

   def __init__(self, name: str="TraderBase", capital: float=10000.0, simulation: bool=True, trading_costs: TradingCosts=ibkr_trading_costs) -> None:
      self.name = name
      self.simulation = simulation
      self.trading_costs = trading_costs
      self.capital = capital
      self.live = False
      self.simulated_save = {}
      # Threading support
      if self.simulation:
         self.bot_lock = LockStub()
      else:
         self.bot_lock = Lock()

      if not self.simulation:
         # Create/open save file
         if not os.path.exists("Save/"):
            os.makedirs("Save/")
         self.save_path = Path("Save/" + self.name + ".json")
         if not self.save_path.is_file():
            print("save does not exist, creating: " + str(self.save_path))
            with open(self.save_path, 'w') as sv:
               sv.write("{}")

   def process(self):
      with self.bot_lock:
         self.watchdog_pet = True
      return self.num_pending

   def order(self, price: float, quantity: int):
      # Open new position
      if self.num_held == 0 and self.num_pending == 0 and self.trading_enabled:
         self.num_pending = quantity
         self.average_price = price # needed to avoid immediate stop loss 
      elif self.num_held != 0 and self.trading_enabled:
         self.num_pending = quantity

      if self.simulation:
            buy = True if quantity > 0 else False
            self.simulate_costs(quantity, price, buy)
            self.confirm_order(price, quantity)

   def confirm_order(self, avg_price: float, quantity: int):
      # Stats
      if self.num_held == 0:
         if quantity < 0:
            self.short_trades += 1
         else:
            self.long_trades += 1
         self.num_trades += 1
      else:
         profit = -(avg_price * quantity + self.average_price * self.num_held)
         self.profit += profit
         if (profit > 0):
            self.win_trades += 1

      # Bookeeping
      self.num_held += quantity # TODO, this should support partial fill, but need some testing
      self.num_pending = 0
      if self.num_held != 0:
         self.average_price = avg_price
      else:
         self.average_price = 0
   
      if not self.simulation:
         logger.info(f"{self.name}: confirm order of {quantity} at {avg_price}")

   def simulate_costs(self, quantity, price, buy):
      fees, slipage = self.trading_costs.compute_cost(quantity, price, buy)
      self.fees += fees
      self.slipage += slipage
      self.total_costs += fees + slipage
      self.profit -= (fees + slipage)
      self.drawdown = min(self.drawdown, self.profit)
   
   @staticmethod
   def compute_share_quantity(price, capital):
      if price != 0:
         return int(capital / price)
      else:
         return 0

   def get_stats(self) -> list:
      if self.num_trades > 0:
         self.win_percent = self.win_trades / self.num_trades
      return self.profit, self.drawdown, self.win_percent, self.num_trades, self.long_trades, self.short_trades, self.stop_trades
   
   def get_parameters(self):
      return ()
   
   def order_msg(self) -> str:
      return self.name
   
   def save_value(self, key, value):
      if self.simulation:
         self.simulated_save[key] = value
         return
      data = None
      with open(self.save_path, "r") as save:
         data = json.load(save)

      data[key] = value

      with open(self.save_path, "w") as save:
         json.dump(data, save)

   def retrieve_value(self, key, default=0):
      if self.simulation:
         if key not in self.simulated_save:
            self.simulated_save[key] = default
         return self.simulated_save[key]
      
      data = None
      with open(self.save_path, "r") as save:
         data = json.load(save)

      if key not in data:
         data[key] = default
         with open(self.save_path, "w") as save:
            json.dump(data, save)

      return data[key]
   
   def cancel_open_position(self):
      self.num_pending = 0
      self.num_held = 0
      self.average_price = 0

class LockStub():
   def __enter__(self):
      pass

   def __exit__(self, type, value, traceback):
      pass