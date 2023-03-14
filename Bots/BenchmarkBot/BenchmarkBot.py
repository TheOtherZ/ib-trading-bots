import logging

from ibapi.wrapper import BarData

from TraderCore.TraderBase import TraderBase
import TraderCore.Indicators as ind
from Simulation.Simulator import simulate_dual_source

class BenchmarkBot(TraderBase):
   def __init__(self, moving_average_window, deviation_threshold, stop_loss, capital: float=15000.0, reinvestment: bool=False, log_file_name: str = "", name: str = "") -> None:
      super().__init__(log_level=logging.WARN, log_file_name=log_file_name, name=name)

      self.deviation_moving_average = ind.MovingAverage(moving_average_window)
      self.deviation = ind.BenchmarkDeviation()
      self.deviation_threshold = deviation_threshold
      self.stop_loss_percent = stop_loss

      self.data_length = moving_average_window
      self.deviation_list = []
      self.trade_active = False
      self.quantity_to_open = 1

      self.capital = capital
      self.reinvest = reinvestment
      self.last_profit = 0


   def process(self, benchmark_bar: BarData, target_bar: BarData):
      deviation = self.deviation.compute(benchmark_bar, target_bar)

      self.deviation_list.append(deviation)
      if len(self.deviation_list) > self.data_length:
         self.deviation_list.pop(0)
         self.trade_active = True

      self.quantity_to_open = self.compute_share_quantity(target_bar.close, self.capital)

      if not self.trade_active:
         return

      self.deviation_moving_average.compute_simple(self.deviation_list)

      if self.deviation_moving_average.value < -self.deviation_threshold and not self.holding:
         self.open_position(target_bar.close, self.quantity_to_open, "long")
      elif self.deviation_moving_average.value > self.deviation_threshold and not self.holding:
         self.open_position(target_bar.close, self.quantity_to_open, "short")

      if self.deviation_moving_average.value < -self.deviation_threshold and self.holding == "short":
         self.close_position(target_bar.close, self.num_held)
      elif self.deviation_moving_average.value > self.deviation_threshold and self.holding == "long":
         self.close_position(target_bar.close, self.num_held)

      # Benchmark up, but target down
      # Benchmark down, but target up
      # Benchmark up more than target
      # Benchmark down more than target

      # stop loss
      if self.holding == "long" and target_bar.close < (self.average_price * (100 - self.stop_loss_percent) / 100.0):
         self.stop_trades += 1
         self.close_position(target_bar.close, self.num_held)
      elif self.holding == "short" and target_bar.close > (self.average_price * (100 + self.stop_loss_percent) / 100.0):
         self.stop_trades += 1
         self.close_position(target_bar.close, self.num_held)

      return super().process()

   def __str__(self):
      return f"{self.deviation_moving_average.window_size}, {self.deviation_threshold}, {self.stop_loss_percent}"

def build_trader_list():
   trader_list = []

   average_window_list = [2, 3, 5, 10]
   deviation_threshold_list = [0.5, 1.0, 2.0, 3.0, 5.0]
   stop_loss_list = [1.5, 2.0, 2.5]

   for average_window in average_window_list:
      for deviation_threshold in deviation_threshold_list:
         for stop_loss in stop_loss_list:
            trader_list.append(BenchmarkBot(average_window, deviation_threshold, stop_loss))

   return trader_list

def simAMD():
   data_2_dir = "/home/zimbra/development/IBBot/Data/AMD_10Min_Bars_Long/"
   data_2_master = "AMD_2020-01-01_2023-01-09_10 mins.txt"
   data_1_dir = "/home/zimbra/development/IBBot/Data/QQQ_10Min_Bars_Long/"
   data_1_master = "QQQ_2020-01-01_2023-01-09_10 mins.txt"

   trader_list = build_trader_list()

   simulate_dual_source(trader_list, data_1_dir, data_1_master, data_2_dir, data_2_master, None, 8)

if __name__ == "__main__":
   simAMD()