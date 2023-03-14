from ibapi.wrapper import BarData
from IBTradingBot import IBTradingBot, TradingCosts
import HelperFunctions as hf
from Indicators import StochasticOscillator

class MicroTraderBot(IBTradingBot):
   def __init__(self, bar_storage_size: int, moving_average_bars: int, stop_loss_percent: float, 
                momentum_window: int, momentum_threshold: float, crossing_count: int, 
                crossing_threshold: float, crossing_margin: float, cost: TradingCosts, 
                capital=5000, simulation=True, printing=False):
      super().__init__(cost, capital, bar_storage_size, simulation, printing)

      # Moving Average, clamp to bar storage size - 1
      self.moving_average_size = moving_average_bars if moving_average_bars < bar_storage_size else bar_storage_size - 1
      self.moving_average = 0

      # Momentum Average
      self.momentum_window_size = momentum_window
      self.momentum_list = [0] * self.momentum_window_size
      self.average_momentum = 0
      self.momentum_threshold = momentum_threshold

      # Crossing Threshold
      self.crossing_count = crossing_count
      self.crossing_list = [0] * self.crossing_count
      self.crossing_threshold = crossing_threshold
      self.crossing_value = 0
      self.crossing_margin = crossing_margin

      # Stop Loss
      self.stop_loss_percent = stop_loss_percent

      # Stochastic oscillator
      self.stochastic_oscillator = StochasticOscillator(28, 3)

      # Preheat ticks
      self.preheat_ticks = max(self.moving_average_size, self.momentum_window_size + 1)
      self.day_tick_count = 0

   def update_moving_average(self):
      total = 0
      for bar in self.bar_list[-self.moving_average_size:]:
         total += bar.average

      self.moving_average = total / self.moving_average_size

   def update_momentum(self):
      momentum = self.bar_list[-2].average - self.bar_list[-1].average
      self.momentum_list.append(momentum)
      self.momentum_list.pop(0)
      self.average_momentum = sum(self.momentum_list) / self.momentum_window_size

   def update_crossing_value(self, last_bar: BarData):
      if last_bar.average > self.moving_average:
         self.crossing_list.append(1)
         self.crossing_list.pop(0)
      elif last_bar.average < self.moving_average:
         self.crossing_list.append(-1)
         self.crossing_list.pop(0)

      self.crossing_value = sum(self.crossing_list) / self.crossing_count

   def compute_open_positions(self, short_price: float, long_price: float):
      stochastic_overheat = self.stochastic_oscillator.fast_value > 70 and self.stochastic_oscillator.slow_value > 70
      stochastic_overcooled = self.stochastic_oscillator.fast_value < 30 and self.stochastic_oscillator.slow_value < 30

      if self.crossing_value > self.crossing_threshold and self.average_momentum >= self.momentum_threshold and stochastic_overcooled:
         self.open_long_position(long_price)
      elif self.crossing_value < -self.crossing_threshold and self.average_momentum <= -self.momentum_threshold and stochastic_overheat:
         self.open_short_position(short_price)

   def compute_close_positions(self, short_price: float, long_price: float):
      #
      if self.position_type == 'long' and self.crossing_value < self.crossing_threshold - self.crossing_margin:
         self.close_long_position(long_price)
      elif self.position_type == 'short' and self.crossing_value > self.crossing_threshold + self.crossing_margin:
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
      self.update_moving_average()
      self.update_momentum()
      self.stochastic_oscillator.compute(underlying_bar)

      self.day_tick_count += 1

      if self.day_tick_count < self.preheat_ticks:
         return
      
      self.update_crossing_value(underlying_bar)

      self.compute_open_positions(short_bar.close, long_bar.close)
      self.compute_close_positions(short_bar.close, long_bar.close)

   def start_new_trading_period(self):
      super().start_new_trading_period()
      self.day_tick_count = 0

   def print_configuration(self):
      print("config: %s, %s, %s, %s, %s, %s, %s, %s" % (self.bar_storage_size, self.moving_average_size, self.stop_loss_percent, self.momentum_window_size, self.momentum_threshold, self.crossing_count, self.crossing_threshold, self.crossing_margin))
      #print("Costs: %s, %s, %s, %s" % (self.trading_costs.commission, self.trading_costs.sec_transaction, self.trading_costs.finra_activity, self.trading_costs.slipage))

if __name__ == "__main__":
   trading_costs = TradingCosts(0.02, 0.005, 0.0000229, 0.00013, 1.00)
   bot = MicroTraderBot(5, 4, 0.5, 3, 0.05, 10, 0.5, 0.05, trading_costs)
   bot.print_stats()
   bot.print_configuration()