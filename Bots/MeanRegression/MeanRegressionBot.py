import logging

from ibapi.wrapper import BarData

from TraderCore.TraderBase import TraderBase
from TraderCore.TradingCosts import ibkr_trading_costs, TradingCosts
import TraderCore.Indicators as ind
from TraderCore.HelperFunctions import compute_percent_threshold

class MeanRegressionBot(TraderBase):
   def __init__(self, average_window: int, momentum_window: int, stop_loss: float, rsi_window: int, profit_take: float, ticker: str, capital: float=15000.0, cost: TradingCosts=ibkr_trading_costs, simulation: bool = True, log_level: int = logging.WARNING, log_file_name: str = "", name: str = "none_bot", leverage: float = 1, save_dir="Save/") -> None:
      super().__init__(cost=cost, log_level=log_level, log_file_name=log_file_name, name=name, save_dir=save_dir, simulation=simulation)

      self.ticker = ticker

      self.purge_count = 4 #TODO: configurable?
      self.remaining_short_purge_bars = 0
      self.remaining_long_purge_bars = 0

      self.moving_average = ind.MovingAverage(average_window)
      self.moving_mass = ind.MovingMass(momentum_window)
      self.rsi = ind.RSIOscillator(rsi_window)

      self.bar_list = []
      self.data_length = average_window + momentum_window
      self.trade_active = False
      self.quantity_to_open = 1

      self.stop_loss = stop_loss
      self.proft_take = profit_take
      self.capital = capital

   
   def process(self, bar: BarData):
      self.bar_list.append(bar)
      if len(self.bar_list) > self.data_length:
         self.bar_list.pop(0)
         if not self.trade_active:
            logging.info(self.name + " Data fill complete, trading active for " + self.ticker)
         self.trade_active = True

      self.moving_average.compute(self.bar_list)
      self.rsi.compute(bar)

      self.quantity_to_open = self.compute_share_quantity(bar.close, self.capital)

      if len(self.bar_list) > self.moving_average.window_size:
         self.moving_mass.compute(self.moving_average.value, bar)

      if self.remaining_short_purge_bars > 0:
         self.remaining_short_purge_bars -= 1

      if self.remaining_long_purge_bars > 0:
         self.remaining_long_purge_bars -= 1
      
      if not self.trade_active:
         return None, None, 0
      
      open_long = self.moving_mass.value < 8 and bar.close < self.moving_average.value and self.rsi.value < 20 and self.remaining_long_purge_bars == 0
      open_short = self.moving_mass.value > 92 and bar.close > self.moving_average.value and self.rsi.value > 80 and self.remaining_short_purge_bars == 0
      
      if self.holding is None:
         if open_long:
            self.open_position(bar.close, self.quantity_to_open, "long")
         elif open_short:
            self.open_position(bar.close, self.quantity_to_open, "short")

      else:
         stop_long = False
         stop_short = False
         # stop_short, stop_long = compute_percent_threshold(self.average_price, bar.close, self.stop_loss)
         # if stop_long:
         #    self.stop_trades += 1
         #    self.remaining_long_purge_bars = self.purge_count # Prevent immediately opening the same position
         # elif stop_short:
         #    self.stop_trades += 1
         #    self.remaining_short_purge_bars = self.purge_count # Prevent immediately opening the same position

         profit_long, profit_short = compute_percent_threshold(self.average_price, bar.close, self.proft_take)

         close = False
         if self.holding == "long" and (stop_long or bar.close >= self.moving_average.value or profit_long):
            if bar.close > self.average_price:
               self.win_trades += 1
            close = True
         elif self.holding == "short" and (stop_short or bar.close <= self.moving_average.value or profit_short):
            if bar.close < self.average_price:
               self.win_trades += 1
            close = True
         
         if close:
            self.close_position(bar.close, self.num_held)

      return super().process(bar)
   
   def confirm_open(self, price: float, quantity: int):
      return super().confirm_open(price, quantity)

   def get_parameters(self):
      return (self.moving_average.window_size, self.moving_mass.mass_window_size, self.stop_loss, self.rsi.period, self.proft_take)

   def __str__(self):
      return f"{self.moving_average.window_size}, {self.moving_mass.mass_window_size}, {self.stop_loss}, {self.rsi.period}, {self.proft_take}"
