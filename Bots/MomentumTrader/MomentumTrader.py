from signal import raise_signal
from ibapi.wrapper import BarData
from IBTradingBot import IBTradingBot, TradingCosts
import HelperFunctions as hf
import Indicators as ind 

class MomentumTraderBot(IBTradingBot):
   def __init__(self, stop_loss_percent, moving_average_window, crossing_window, crossing_threshold, crossing_margin, velocity_window, velocity_threshold, cost: TradingCosts, 
                capital, bar_storage_size=120, simulation=True, printing=False):
      super().__init__(cost, capital, bar_storage_size, simulation, printing)
      self.stop_loss_percent = stop_loss_percent

      # Moving Average
      self.moving_average_window = moving_average_window
      self.moving_average_calculator = ind.MovingAverage(self.moving_average_window)
      self.moving_average = 0

      # Crossing List
      self.crossing_window = crossing_window
      self.crossing_threshold = crossing_threshold
      self.crossing_margin = crossing_margin
      self.crossing_oscillator = ind.CrossingMomentum(self.crossing_window)

      # Price Velocity
      self.velocity_window = velocity_window
      self.price_velocity_threshold = velocity_threshold
      self.price_velocity = ind.Derivative(self.velocity_window)

      # RSI
      self.rsi_oscillator = ind.RSIOscillator(28)

      # Preheat ticks
      self.preheat_ticks = max(self.moving_average_window, self.velocity_window)
      self.day_tick_count = 0
     
   def compute_open_positions(self, short_price: float, long_price: float):
      if self.crossing_oscillator.value > self.crossing_threshold and self.price_velocity.value > self.price_velocity_threshold:
         self.open_long_position(long_price)
      elif self.crossing_oscillator.value < -self.crossing_threshold and self.price_velocity.value < -self.price_velocity_threshold:
         self.open_short_position(short_price)

   def compute_close_positions(self, short_price: float, long_price: float):
      #
      if self.position_type == 'long' and self.crossing_oscillator.value < self.crossing_threshold - self.crossing_margin:
         self.close_long_position(long_price)
      elif self.position_type == 'short' and self.crossing_oscillator.value > -self.crossing_threshold + self.crossing_margin:
         self.close_short_position(short_price)

      # stop loss
      if long_price < (self.held_position_price * (100 - self.stop_loss_percent) / 100.0) and self.position_type == 'long':
         self.stop_trades += 1
         self.close_long_position(long_price)
      elif short_price < (self.held_position_price * (100 - self.stop_loss_percent) / 100.0) and self.position_type == 'short':
         self.stop_trades += 1
         self.close_short_position(short_price)


   def on_bar_update(self, underlying_bar: BarData, short_bar: BarData, long_bar: BarData):
      self.update_bar_list(underlying_bar)
      self.moving_average = self.moving_average_calculator.compute(self.bar_list)
      self.price_velocity.compute(underlying_bar.wap)
      self.rsi_oscillator.compute(underlying_bar)

      self.day_tick_count += 1

      if self.day_tick_count < self.preheat_ticks or not self.trading_enabled:
         return

      self.crossing_oscillator.compute(self.moving_average, underlying_bar)

      self.compute_open_positions(short_bar.close, long_bar.close)
      self.compute_close_positions(short_bar.close, long_bar.close)

   def start_new_trading_period(self):
      super().start_new_trading_period()
      self.day_tick_count = 0

   def print_configuration(self):
      print("config: %s, %s, %s, %s, %s, %s, %s" % (self.stop_loss_percent, self.moving_average_window, self.crossing_window, self.crossing_threshold, self.crossing_margin, self.velocity_window, self.price_velocity_threshold))
