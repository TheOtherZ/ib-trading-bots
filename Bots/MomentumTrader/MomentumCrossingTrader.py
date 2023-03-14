from signal import raise_signal
from ibapi.wrapper import BarData
from TraderCore.IBTradingBot import IBTradingBot, TradingCosts
import TraderCore.HelperFunctions as hf
import TraderCore.Indicators as ind 

class MomentumCrossingBot(IBTradingBot):
   def __init__(self, stop_loss_percent, moving_average_window, crossing_window, crossing_threshold,
                rsi_period, rsi_signal, rsi_open, cost: TradingCosts, capital, bar_storage_size=120, simulation=True, printing=False):
      super().__init__(cost, capital, bar_storage_size, simulation, printing)
      self.set_parameters(stop_loss_percent, moving_average_window, crossing_window, crossing_threshold, rsi_period, rsi_signal, rsi_open)

   def set_parameters(self, stop_loss_percent, moving_average_window, crossing_window, crossing_threshold,
                      rsi_period, rsi_signal, rsi_open):
      self.stop_loss_percent = stop_loss_percent

      # Moving Average
      self.moving_average_window = moving_average_window
      self.moving_average_calculator = ind.MovingAverage(self.moving_average_window)
      self.moving_average = 0

      # Crossing List
      self.crossing_window = crossing_window
      self.crossing_threshold = crossing_threshold
      self.crossing_buy = False
      self.crossing_sell = False
      self.begin_crossing_compute = False
      self.crossing_momentum_calculator = ind.CrossingMomentum(self.crossing_window)

      # RSI
      self.rsi_period = rsi_period
      self.rsi_signal = rsi_signal
      
      self.rsi_overheat = False
      self.rsi_overcool = False
      self.rsi_oscillator = ind.RSIOscillator(self.rsi_period)

      # Stochastic? NOPE
      self.rsi_open = rsi_open

      # Preheat ticks
      self.preheat_ticks = max(self.moving_average_window, self.rsi_period)
      self.day_tick_count = 0
      

   def update_signals(self):
      # Crossing signal
      if self.crossing_momentum_calculator.value > self.crossing_threshold:
         self.crossing_buy = True
         self.crossing_sell = False
      elif self.crossing_momentum_calculator.value < -self.crossing_threshold:
         self.crossing_buy = False
         self.crossing_sell = True
      else:
         self.crossing_buy = False
         self.crossing_sell = False

      # RSI
      if self.rsi_oscillator.value > (100 - self.rsi_signal):
         self.rsi_overheat = True
         self.rsi_overcool = False
      elif self.rsi_oscillator.value < self.rsi_signal:
         self.rsi_overheat = False
         self.rsi_overcool = True
      else:
         self.rsi_overheat = False
         self.rsi_overcool = False
     
   def compute_open_positions(self, short_price: float, long_price: float):
      if self.crossing_buy and self.rsi_oscillator.value < self.rsi_open:
         self.open_long_position(long_price)
      elif self.crossing_sell and self.rsi_oscillator.value > (100 - self.rsi_open):
         self.open_short_position(short_price)

   def compute_close_positions(self, short_price: float, long_price: float):
      #
      if self.position_type == 'long' and self.rsi_overheat:
         self.close_long_position(long_price)
      elif self.position_type == 'short' and self.rsi_overcool:
         self.close_short_position(short_price)

      # stop loss
      if long_price < (self.held_position_price * (100 - self.stop_loss_percent) / 100.0) and self.position_type == 'long':
         self.stop_trades += 1
         self.close_long_position(long_price)
         self.day_tick_count = 0
         #self.disable_buying() # Done for now
      elif short_price < (self.held_position_price * (100 - self.stop_loss_percent) / 100.0) and self.position_type == 'short':
         self.stop_trades += 1
         self.close_short_position(short_price)
         self.day_tick_count = 0
         #self.disable_buying() # Done for now


   def on_bar_update(self, underlying_bar: BarData, short_bar: BarData, long_bar: BarData):
      self.update_bar_list(underlying_bar)
      self.moving_average = self.moving_average_calculator.compute(self.bar_list)
      self.rsi_oscillator.compute(underlying_bar)
      self.update_signals()

      # Allow day pauses
      if self.begin_crossing_compute:
         self.crossing_momentum_calculator.compute(self.moving_average, underlying_bar)

      self.day_tick_count += 1

      if self.day_tick_count < self.preheat_ticks or not self.trading_enabled:
         return
      self.begin_crossing_compute = True

      self.compute_open_positions(short_bar.close, long_bar.close)
      self.compute_close_positions(short_bar.close, long_bar.close)

   def start_new_trading_period(self):
      super().start_new_trading_period()
      self.rsi_oscillator.reset()
      self.day_tick_count = 0
      self.begin_crossing_compute = False

   def print_configuration(self):
      print("config: %s, %s, %s, %s, %s, %s, %s" % (self.stop_loss_percent, self.moving_average_window, self.crossing_window, self.crossing_threshold, self.rsi_period, self.rsi_signal, self.rsi_open))
