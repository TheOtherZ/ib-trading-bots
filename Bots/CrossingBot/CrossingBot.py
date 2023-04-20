import json
import logging

from ibapi.wrapper import BarData

from TraderCore.TraderBase import TraderBase
import TraderCore.Indicators as ind

class CrossingBot(TraderBase):
   def __init__(self, average_window, crossing_window, crossing_threshold, stop_loss, rsi_window, purge_bars=0, sell_rsi_window=8, sell_crossing_threshold=-1.0, 
                strange_mode=True, capital: float=15000.0, reinvestment: bool=False, log_file_name: str = "", name: str = "", log_level=logging.WARN, save_dir: str="Save/", simulation=True) -> None:
      super().__init__(log_level=log_level, log_file_name=log_file_name, name=name, save_dir=save_dir, simulation=simulation)

      self.moving_average = ind.MovingAverage(average_window)
      self.price_crossing = ind.CrossingMomentum(crossing_window)
      self.rsi = ind.RSIOscillator(rsi_window)
      self.sell_rsi = ind.RSIOscillator(sell_rsi_window)
      self.crossing_threshold = crossing_threshold
      self.strange_mode = strange_mode
      if strange_mode:
         self.sell_crossing_threshold = -1
      else:
         self.sell_crossing_threshold = sell_crossing_threshold

      self.stop_loss_percent = stop_loss
      self.purge_bars = purge_bars
      self.purge_count = 0

      if not self.simulation:
         data = None
         save = open(self.save_name, "r")
         data = json.load(save)
         save.close()
         if "purge_count" in data:
               self.purge_count = int(data["purge_count"])
         else:
            data["purge_count"] = 0

         save = open(self.save_name, "w")
         json.dump(data, save)
         save.close()

      self.bar_list = []
      self.data_length = average_window + crossing_window
      self.trade_active = False
      self.quantity_to_open = 1

      self.capital = capital
      self.reinvest = reinvestment
      self.last_profit = 0

   def process(self, bar: BarData):
      self.bar_list.append(bar)
      if len(self.bar_list) > self.data_length:
         self.bar_list.pop(0)
         if not self.trade_active:
            logging.info("Data fill complete, trading active")
         self.trade_active = True

      self.rsi.compute(bar)
      self.sell_rsi.compute(bar)
      self.quantity_to_open = self.compute_share_quantity(bar.close, self.capital)

      if self.purge_count > 0 and self.trade_active:
         self.purge_count -= 1
         self.save_value("purge_count", self.purge_count)
      
      self.moving_average.compute(self.bar_list)

      if len(self.bar_list) > self.moving_average.window_size:
         self.price_crossing.compute(self.moving_average.value, bar)
      
      if not self.simulation and self.trade_active and self.trading_enabled:
         print(f"{self.name}- Crossing: {self.price_crossing.value},Buy RSI: {self.rsi.value}, Sell RSI: {self.sell_rsi.value}, Holding: {self.holding}")

      if not self.trade_active or self.purge_count > 0:
         return None, None, 0
      
      open_long = self.price_crossing.value <= self.crossing_threshold and self.rsi.value <= 20
      open_short = self.price_crossing.value >= -self.crossing_threshold and self.rsi.value >= 80

      if open_long:
         self.open_position(bar.close, self.quantity_to_open, "long")
      elif open_short:
         self.open_position(bar.close, self.quantity_to_open, "short")

      # elif self.holding == 'long' and self.sell_rsi.value >= 80:
      #    self.close_position(bar.close, self.num_held)
      # elif self.holding == 'short' and self.sell_rsi.value <= 20:
      #    self.close_position(bar.close, self.num_held)

      close_long = self.price_crossing.value >= self.sell_crossing_threshold and self.sell_rsi.value >= 80
      close_short = self.price_crossing.value <= -self.sell_crossing_threshold and self.sell_rsi.value <= 20

      if self.holding == 'long' and (not open_long or not self.strange_mode) and (not open_short or not self.strange_mode) and close_long:
         self.close_position(bar.close, self.num_held)
      elif self.holding == 'short' and (not open_long or not self.strange_mode) and (not open_short or not self.strange_mode) and close_short:
         self.close_position(bar.close, self.num_held)

      # if self.holding == 'long' and close_long:
      #    self.close_position(bar.close, self.num_held)
      # elif self.holding == 'short' and close_short:
      #    self.close_position(bar.close, self.num_held)

      # stop loss
      if self.holding == "long" and bar.close < (self.average_price * (100 - self.stop_loss_percent) / 100.0):
         self.stop_trades += 1
         logging.info(f"Stop loss triggered on long position")
         self.close_position(bar.close, self.num_held)
         self.purge_count = self.purge_bars
         self.save_value("purge_count", self.purge_count)
      elif self.holding == "short" and bar.close > (self.average_price * (100 + self.stop_loss_percent) / 100.0):
         self.stop_trades += 1
         logging.info(f"Stop loss triggered on short position")
         self.close_position(bar.close, self.num_held)
         self.purge_count = self.purge_bars
         self.save_value("purge_count", self.purge_count)

      # Re-invest profit
      if self.reinvest and self.profit > self.last_profit:
         self.capital += (self.profit - self.last_profit)

      if self.profit > self.last_profit:
         self.last_profit = self.profit
      
      return super().process(bar)
   
   def get_parameters(self):
      return (self.moving_average.window_size, len(self.price_crossing.crossing_list), self.crossing_threshold, self.stop_loss_percent, self.rsi.period, self.purge_bars, self.sell_rsi.period, self.sell_crossing_threshold, self.strange_mode)

   def __str__(self):
      return f"{self.moving_average.window_size}, {len(self.price_crossing.crossing_list)}, {self.crossing_threshold}, {self.stop_loss_percent}, {self.rsi.period}, {self.purge_bars}, {self.sell_rsi.period}, {self.sell_crossing_threshold}, {self.strange_mode}"
