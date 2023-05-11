from TraderCore.TradingCosts import TradingCosts, ibkr_trading_costs

import logging
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

   # Trading costs
   total_costs = 0
   slipage = 0
   fees = 0

   def __init__(self, name: str="TraderBase", capital: float=10000.0, simulation: bool=True, trading_costs: TradingCosts=ibkr_trading_costs) -> None:
      self.name = name
      self.simulation = simulation
      self.trading_costs = trading_costs
      self.capital = capital

   def process(self):
      return self.num_pending

   def order(self, price: float, quantity: int):
      # Open new position
      if self.num_held == 0 and self.num_pending == 0 and self.trading_enabled:
         self.num_pending = quantity
         self.average_price = price # needed to avoid immediate stop loss 
      elif self.num_held != 0:
         self.num_pending = quantity

      if self.simulation:
            buy = True if quantity > 0 else False
            self.simulate_costs(quantity, price, buy)
            self.confirm_order(price, quantity)
      else:
         logger.info(f"{self.name}: order of {quantity} at {price}")

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
