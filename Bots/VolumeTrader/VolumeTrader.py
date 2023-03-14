from signal import raise_signal
from ibapi.wrapper import BarData
from IBTradingBot import IBTradingBot, TradingCosts
import HelperFunctions as hf
from Indicators import RSIOscillator, StochasticOscillator, VolumeRSIOscillator, EZVolume

class VolumeTraderBot(IBTradingBot):
   def __init__(self, stop_loss_percent, volume_rsi_window, lookback_window, cost: TradingCosts, capital, bar_storage_size=120, simulation=True, printing=False):
      super().__init__(cost, capital, bar_storage_size, simulation, printing)

      self.stop_loss_percent = stop_loss_percent

      # Volume RSI
      self.volume_rsi_window = volume_rsi_window
      self.look_back_window_size = lookback_window
      self.lookback_volume_rsi_list = [50] * self.look_back_window_size
      self.volume_rsi_oscillator = EZVolume(volume_rsi_window)
      self.volume_rsi_short_long = None
      self.last_over_count = 0

      # Preheat
      self.preheat_ticks = max(self.volume_rsi_window, self.look_back_window_size)
      self.day_tick_count = 0

   def update_indicators(self, last_bar: BarData):
      # Volume RSI Oscillator
      volume_rsi_value = self.volume_rsi_oscillator.compute(last_bar)
      self.lookback_volume_rsi_list.append(volume_rsi_value)
      self.lookback_volume_rsi_list.pop(0)
      
      over_count = 0
      for val in self.lookback_volume_rsi_list:
         if val > 50:
            over_count += 1
         else:
            over_count -= 1

      if over_count > 0 and self.last_over_count < 0:
         self.volume_rsi_short_long = "long"
      elif over_count < 0 and self.last_over_count > 0:
         self.volume_rsi_short_long = "short"
      else:
         self.volume_rsi_short_long = None
      self.last_over_count = over_count

   
   def compute_open_positions(self, short_price: float, long_price: float):
      if self.volume_rsi_short_long == 'long':
         self.open_long_position(long_price)
      elif self.volume_rsi_short_long == 'short':
         self.open_short_position(short_price)


   def compute_close_positions(self, short_price: float, long_price: float):
      #
      if self.position_type == 'long' and self.volume_rsi_short_long == 'short':
         self.close_long_position(long_price)
      elif self.position_type == 'short' and self.volume_rsi_short_long == 'long':
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
      self.update_indicators(underlying_bar)

      self.day_tick_count += 1

      if self.day_tick_count < self.preheat_ticks:
         return
   
      self.compute_open_positions(short_bar.close, long_bar.close)
      self.compute_close_positions(short_bar.close, long_bar.close)

   def start_new_trading_period(self):
      super().start_new_trading_period()
      self.day_tick_count = 0

   def print_configuration(self):
      print("config: %s, %s" % (self.volume_rsi_window ,self.look_back_window_size))
      