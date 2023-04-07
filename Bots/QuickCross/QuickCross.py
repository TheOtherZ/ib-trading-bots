import json
import logging

from ibapi.wrapper import BarData

from TraderCore.TraderBase import TraderBase
import TraderCore.Indicators as ind

class QuickCross(TraderBase):
   def __init__(self, average_window, crossing_window, crossing_threshold, stop_loss, rsi_window, profit_horizon, profit_take, num_bars_in_day=39, capital: float=15000.0, log_file_name: str = "", name: str = "", log_level=logging.WARN, save_dir: str="Save/", simulation=True) -> None:
      super().__init__(log_level=log_level, log_file_name=log_file_name, name=name, save_dir=save_dir, simulation=simulation)

      self.moving_average = ind.MovingAverage(average_window)
      self.price_crossing = ind.CrossingMomentum(crossing_window)

      self.profit_horizon_bars = profit_horizon
      self.remaining_profit_bars = 0

      self.rsi = ind.RSIOscillator(rsi_window)
      self.crossing_threshold = crossing_threshold

      #Stochastic
      self.stochastic = ind.StochasticOscillator(3, 8)

      self.stop_loss_percent = stop_loss
      self.profit_take = profit_take

      # Bar counting
      self.num_bars_in_day = num_bars_in_day
      self.bar_count = 0

      self.bar_list = []
      self.data_length = average_window + crossing_window
      self.trade_active = False
      self.quantity_to_open = 1

      self.capital = capital

   def process(self, bar: BarData):
      self.bar_list.append(bar)
      if len(self.bar_list) > self.data_length:
         self.bar_list.pop(0)
         if not self.trade_active:
            logging.info("Data fill complete, trading active")
         self.trade_active = True

      self.rsi.compute(bar)
      self.stochastic.compute(bar)
      self.quantity_to_open = self.compute_share_quantity(bar.close, self.capital)
      
      self.moving_average.compute(self.bar_list)

      if len(self.bar_list) > self.moving_average.window_size:
         self.price_crossing.compute(self.moving_average.value, bar)
      
      # if not self.simulation and self.trade_active and self.trading_enabled:
      #    print(f"{self.name}- Crossing: {self.price_crossing.value},Buy RSI: {self.rsi.value}, Sell RSI: {self.sell_rsi.value}, Holding: {self.holding}")

      self.bar_count += 1
      if self.simulation and self.bar_count % self.num_bars_in_day == 0:
         self.bar_count = 0

      if not self.trade_active:
         return None, None, 0
      
      open_long = self.price_crossing.value >= self.crossing_threshold and self.rsi.value <= 15 and self.stochastic.fast_value <= 20 and self.stochastic.slow_value <= 20
      open_short = self.price_crossing.value <= -self.crossing_threshold and self.rsi.value >= 85 and self.stochastic.fast_value >= 80 and self.stochastic.slow_value >= 80

      if open_long and self.bar_count <= self.num_bars_in_day - self.profit_horizon_bars:
         self.open_position(bar.close, self.quantity_to_open, "long")
      elif open_short and self.bar_count <= self.num_bars_in_day - self.profit_horizon_bars:
         self.open_position(bar.close, self.quantity_to_open, "short")

      if self.holding == "long" and bar.close > (self.average_price * (100 + self.profit_take) / 100.0):
         self.win_trades += 1
         self.close_position(bar.close, self.num_held)
      elif self.holding == "short" and bar.close < (self.average_price * (100 - self.profit_take) / 100.0):
         self.win_trades += 1
         self.close_position(bar.close, self.num_held)

      if self.remaining_profit_bars > 0:
         self.remaining_profit_bars -= 1
      elif self.remaining_profit_bars == 0 and self.holding is not None and self:
         # Opportunity over, close position
         self.compute_win(bar.close)
         self.close_position(bar.close, self.num_held)
         #self.stop_trades += 1 should this be counted as a stop?

      # stop loss
      if self.holding == "long" and bar.close < (self.average_price * (100 - self.stop_loss_percent) / 100.0):
         self.stop_trades += 1
         logging.info(f"Stop loss triggered on long position")
         self.close_position(bar.close, self.num_held)
      elif self.holding == "short" and bar.close > (self.average_price * (100 + self.stop_loss_percent) / 100.0):
         self.stop_trades += 1
         logging.info(f"Stop loss triggered on short position")
         self.close_position(bar.close, self.num_held)
      
      return super().process(bar)
   
   def confirm_close(self, price: float, quantity: int):
      return super().confirm_close(price, quantity)
   
   def confirm_open(self, price: float, quantity: int):
      self.remaining_profit_bars = self.profit_horizon_bars
      if self.simulation:
         self.remaining_profit_bars += 1 # need extra bar because in sim the order is confirmed in same process loop as open
      return super().confirm_open(price, quantity)
   
   def compute_win(self, price):
      if self.holding == "long" and self.average_price < price:
         self.win_trades += 1
      if self.holding == "short" and self.average_price > price:
         self.win_trades += 1
   
   def get_parameters(self):
      return (self.moving_average.window_size, len(self.price_crossing.crossing_list), self.crossing_threshold, self.stop_loss_percent, self.rsi.period, self.profit_horizon_bars, self.profit_take)

   def __str__(self):
      return f"{self.moving_average.window_size}, {len(self.price_crossing.crossing_list)}, {self.crossing_threshold}, {self.stop_loss_percent}, {self.rsi.period}, {self.profit_horizon_bars}, {self.profit_take}"
