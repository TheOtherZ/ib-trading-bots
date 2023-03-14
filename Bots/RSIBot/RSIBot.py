import logging

from ibapi.wrapper import BarData

from TraderCore.TraderBase import TraderBase
import TraderCore.Indicators as ind
from Simulation.Simulator import simulate_single_source

class RSIBot(TraderBase):
   def __init__(self, long_period, short_period, overbought, oversold, stop_loss=2.0, log_file_name: str="", name: str="", capital: float=15000.0) -> None:
      super().__init__(log_level=logging.WARN, log_file_name=log_file_name, name=name)
      self.long_rsi = ind.RSIOscillator(long_period)
      self.short_rsi = ind.RSIOscillator(short_period)
      self.overbought = overbought
      self.oversold = oversold
      self.stop_loss_percent = stop_loss

      self.bar_list = []
      self.data_length = long_period
      self.trade_active = False
      self.quantity_to_open = 1
      self.capital = capital

   def process(self, bar: BarData):
      self.bar_list.append(bar)
      if len(self.bar_list) > self.data_length:
         self.bar_list.pop(0)
         self.trade_active = True
      self.long_rsi.compute(bar)
      self.short_rsi.compute(bar)

      self.quantity_to_open = self.compute_share_quantity(bar.close, self.capital)

      if not self.trade_active:
         return
      
      # Open positions
      if self.holding is None and self.long_rsi.value < self.oversold and self.short_rsi.value < self.oversold:
         self.open_position(bar.close, self.quantity_to_open, "long")
      elif self.holding is None and self.long_rsi.value > self.overbought and self.short_rsi.value > self.overbought:
         self.open_position(bar.close, self.quantity_to_open, "short")

      # Close based on short term rsi only?
      if self.holding == "short" and self.short_rsi.value < self.oversold:
         self.close_position(bar.close, self.num_held)
      elif self.holding == "long" and self.short_rsi.value > self.overbought:
         self.close_position(bar.close, self.num_held)

      # stop loss
      if self.holding == "long" and bar.close < (self.average_price * (100 - self.stop_loss_percent) / 100.0):
         self.stop_trades += 1
         self.close_position(bar.close, self.num_held)
      elif self.holding == "short" and bar.close > (self.average_price * (100 + self.stop_loss_percent) / 100.0):
         self.stop_trades += 1
         self.close_position(bar.close, self.num_held)

   def __str__(self):
      return f"{self.long_rsi.period}, {self.short_rsi.period}, {self.overbought}, {self.oversold}, {self.stop_loss_percent}"

def simAMD():
   print("Simulating with AMD")
   # data_1_dir = "/home/zimbra/development/IBBot/Data/AMD_10Min_Bars/"
   # data_1_master = "AMD_2022-01-01_2023-01-09_10 mins.txt"

   data_1_dir = "/home/zimbra/development/IBBot/Data/AMD_10Min_Bars_Long/"
   data_1_master = "AMD_2020-01-01_2023-01-09_10 mins.txt"

   # data_1_dir = "/home/zimbra/development/IBBot/Data/AMD_5Min_Bars/"
   # data_1_master = "AMD_2022-01-01_2023-01-09_5 mins.txt"

   trader_list = []

   long_period_list = [4, 9, 12, 24]
   short_period_list = [3, 5, 8, 10, 14]
   overbought_list = [75, 80, 85, 90]
   oversold_list = [10, 15, 20, 25]
   stop_loss_list = [1.5, 2.0, 2.5, 3.0]

   for long_period in long_period_list:
      for short_period in short_period_list:
         for overbought in overbought_list:
            for oversold in oversold_list:
               for stop_loss in stop_loss_list:
                  if long_period >= short_period:
                     trader_list.append(RSIBot(long_period, short_period, overbought, oversold, stop_loss))

   simulate_single_source(trader_list, data_1_dir, data_1_master, None, 8)

def simQQQ():
   print("Simulating with QQQ")
   data_1_dir = "/home/zimbra/development/IBBot/Data/QQQ_10Min_Bars/"
   data_1_master = "QQQ_2022-01-01_2022-10-27_10 mins.txt"

   # data_1_dir = "/home/zimbra/development/IBBot/Data/AMD_5Min_Bars/"
   # data_1_master = "AMD_2022-01-01_2023-01-09_5 mins.txt"

   trader_list = []

   long_period_list = [4, 9, 12, 24]
   short_period_list = [3, 5, 8, 10, 14]
   overbought_list = [75, 80, 85]
   oversold_list = [15, 20, 25]
   stop_loss_list = [1.5, 2.0, 2.5]

   for long_period in long_period_list:
      for short_period in short_period_list:
         for overbought in overbought_list:
            for oversold in oversold_list:
               for stop_loss in stop_loss_list:
                  if long_period >= short_period:
                     trader_list.append(RSIBot(long_period, short_period, overbought, oversold, stop_loss))

   simulate_single_source(trader_list, data_1_dir, data_1_master, None, 8)

def simINTC():
   print("Simulating with INTC")

   data_1_dir = "/home/zimbra/development/IBBot/Data/INTC_10Min_Bars_Long/"
   data_1_master = "INTC_2020-01-01_2023-01-09_10 mins.txt"

   trader_list = []

   long_period_list = [4, 9, 12, 24]
   short_period_list = [3, 5, 8, 10, 14]
   overbought_list = [75, 80, 85, 90]
   oversold_list = [10, 15, 20, 25]
   stop_loss_list = [1.5, 2.0, 2.5, 3.0]

   for long_period in long_period_list:
      for short_period in short_period_list:
         for overbought in overbought_list:
            for oversold in oversold_list:
               for stop_loss in stop_loss_list:
                  if long_period >= short_period:
                     trader_list.append(RSIBot(long_period, short_period, overbought, oversold, stop_loss))

   simulate_single_source(trader_list, data_1_dir, data_1_master, None, 8)

if __name__ == "__main__":
   #simAMD()
   simINTC()
   #simQQQ()