import logging

from ibapi.wrapper import BarData

from TraderCore.TraderBase import TraderBase
from TraderCore.TradingCosts import ibkr_trading_costs, TradingCosts
import TraderCore.Indicators as ind
from TraderCore.HelperFunctions import compute_percent_threshold

class MeanRegressionBot(TraderBase):
   def __init__(self, average_window: int, momentum_window: int, stop_loss: float, rsi_window: int, profit_horizon: int, ticker: str, capital: float=15000.0, cost: TradingCosts=ibkr_trading_costs, simulation: bool = True, log_level: int = logging.WARNING, log_file_name: str = "", name: str = "none_bot", leverage: float = 1, save_dir="Save/") -> None:
      super().__init__(cost=cost, log_level=log_level, log_file_name=log_file_name, name=name, save_dir=save_dir, simulation=simulation)

      self.ticker = ticker

      self.profit_horizon = profit_horizon
      self.remaining_profit_bars = 0 #TODO: will need to save to NVM

      self.purge_count = profit_horizon #TODO: seperate value?
      self.remaining_bars_to_purge = 0

      self.moving_average = ind.MovingAverage(average_window)
      self.moving_mass = ind.MovingMass(momentum_window)
      self.rsi = ind.RSIOscillator(rsi_window)

      self.bar_list = []
      self.data_length = average_window + momentum_window
      self.trade_active = False
      self.quantity_to_open = 1

      self.stop_loss = stop_loss
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

      if self.remaining_bars_to_purge > 0:
         self.remaining_bars_to_purge -= 1
      
      if not self.trade_active or self.remaining_bars_to_purge != 0:
         return None, None, 0
      
      if self.holding is None:
         if self.moving_mass.value < 10 and bar.close < self.moving_average.value and self.rsi.value < 20:
            self.open_position(bar.close, self.quantity_to_open, "long")
         elif self.moving_mass.value > 90 and bar.close > self.moving_average.value and self.rsi.value > 80:
            self.open_position(bar.close, self.quantity_to_open, "short")

      else:
         stop_long, stop_short = compute_percent_threshold(self.average_price, bar.close, self.stop_loss)
         if stop_long or stop_short:
            self.stop_trades += 1
            self.remaining_bars_to_purge = self.purge_count

         close = False
         if self.holding == "long" and (stop_long or bar.close >= self.moving_average.value):
            if bar.close > self.average_price:
               self.win_trades += 1
            close = True
         elif self.holding == "short" and (stop_short or bar.close <= self.moving_average.value):
            if bar.close < self.average_price:
               self.win_trades += 1
            close = True
         
         if close:
            self.close_position(bar.close, self.num_held)

      return super().process(bar)


   def get_parameters(self):
      return (self.moving_average.window_size, self.moving_mass.mass_window_size, self.stop_loss, self.rsi.period, self.profit_horizon)

   def __str__(self):
      return f"{self.moving_average.window_size}, {self.moving_mass.mass_window_size}, {self.stop_loss}, {self.rsi.period}, {self.profit_horizon}"
