import logging

from ibapi.wrapper import BarData

from TraderCore.TraderBase import TraderBase
import TraderCore.Indicators as ind
from Simulation.Simulator import simulate_single_source, simulate_ticker_group, simulate_single_bar_file, simulate_single_trader

import json

class CrossingBot(TraderBase):
   def __init__(self, average_window, crossing_window, crossing_threshold, stop_loss, rsi_window, purge_bars=0, sell_rsi_window=8, capital: float=15000.0, reinvestment: bool=False, log_file_name: str = "", name: str = "", log_level=logging.WARN, save_dir: str="Save/", simulation=True) -> None:
      super().__init__(log_level=log_level, log_file_name=log_file_name, name=name, save_dir=save_dir, simulation=simulation)

      self.moving_average = ind.MovingAverage(average_window)
      self.price_crossing = ind.CrossingMomentum(crossing_window)
      self.rsi = ind.RSIOscillator(rsi_window)
      self.sell_rsi = ind.RSIOscillator(sell_rsi_window)
      self.crossing_threshold = crossing_threshold
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
      

      if self.price_crossing.value <= self.crossing_threshold and self.rsi.value <= 20:
         self.open_position(bar.close, self.quantity_to_open, "long")
      elif self.price_crossing.value >= -self.crossing_threshold and self.rsi.value >= 80:
         self.open_position(bar.close, self.quantity_to_open, "short")

      elif self.holding == 'long' and self.sell_rsi.value >= 80:
         self.close_position(bar.close, self.num_held)
      elif self.holding == 'short' and self.sell_rsi.value <= 20:
         self.close_position(bar.close, self.num_held)

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
      return (self.moving_average.window_size, len(self.price_crossing.crossing_list), self.crossing_threshold, self.stop_loss_percent, self.rsi.period, self.purge_bars, self.sell_rsi.period)

   def __str__(self):
      return f"{self.moving_average.window_size}, {len(self.price_crossing.crossing_list)}, {self.crossing_threshold}, {self.stop_loss_percent}, {self.rsi.period}, {self.purge_bars}, {self.sell_rsi.period}"

def build_trader_list(frame="short"):
   trader_list = []

   if frame == "short":
      average_window_list = [4, 9, 12, 20]
      crossing_window_list = [3, 5, 8, 10]
      crossing_threshold_list = [.1, .2, .3]
      stop_loss_list = [1.0, 1.5, 2.0, 2.5]
      rsi_list = [4, 8, 12]
      purge_list = [5, 10, 15]
      sell_rsi_list = [4, 8, 12]
      # : Profit: 26726.737535369946, Trades: (449, 224, 225), Drawdown: -12.706808724, Stops: 86, Costs: 7511.402464630005
      # 20, 5, 0.1, 2.5, 4, 5, 4
      # : Profit: 22462.61948871804, Trades: (518, 256, 262), Drawdown: -12.706808724, Stops: 171, Costs: 8697.77051128199
      # 20, 5, 0.1, 1.5, 4, 10, 4
      # : Profit: 21940.553019216964, Trades: (445, 221, 224), Drawdown: -12.706808724, Stops: 91, Costs: 7438.826980783007
      # 20, 5, 0.1, 2.5, 4, 10, 4
      # : Profit: 21612.186958272945, Trades: (434, 216, 218), Drawdown: -12.706808724, Stops: 90, Costs: 7236.813041727007
      # 20, 5, 0.1, 2.5, 4, 15, 4
      # : Profit: 20481.302633472016, Trades: (477, 237, 240), Drawdown: -12.706808724, Stops: 129, Costs: 7969.127366527998
      # 20, 5, 0.1, 2.0, 4, 10, 4
   elif frame == "fast":
      average_window_list = [9, 12]
      crossing_window_list = [5, 8]
      crossing_threshold_list = [.2, .3]
      stop_loss_list = [1.0, 2.0]
      rsi_list = [4, 8]
      purge_list = [10, 15]
      sell_rsi_list = [8, 12]
   else:
      average_window_list = [40, 60, 80]
      crossing_window_list = [40, 60, 80, 100]
      crossing_threshold_list = [.3]
      stop_loss_list = [1.0, 2.0, 2.5, 3.0]
      rsi_list = [8, 12, 24, 36]
      purge_list = [10, 15, 25, 35]
      sell_rsi_list = [8, 12, 24]
      # Completed in 391.8914668560028
      # : Profit: 25088.41490964002, Trades: (146, 76, 70), Drawdown: -460.93313255200155, Stops: 56, Costs: 2389.955090360001
      # 80, 40, 0.3, 2.0, 8, 10, 8
      # : Profit: 24324.583954613023, Trades: (140, 75, 65), Drawdown: -460.93313255200155, Stops: 54, Costs: 2257.2960453870005
      # 80, 40, 0.3, 2.0, 8, 15, 8
      # : Profit: 23343.636932716046, Trades: (127, 68, 59), Drawdown: -460.93313255200155, Stops: 56, Costs: 2004.583067284001
      # 60, 60, 0.3, 2.0, 8, 10, 8
      # : Profit: 23002.557409953017, Trades: (143, 76, 67), Drawdown: -460.93313255200155, Stops: 59, Costs: 2314.8025900470006
      # 100, 40, 0.4, 2.0, 8, 10, 8
      # : Profit: 22986.36252354602, Trades: (140, 76, 64), Drawdown: -460.93313255200155, Stops: 54, Costs: 2247.577476454001
      # 80, 40, 0.4, 2.0, 8, 10, 8

   for average_window in average_window_list:
      for crossing_window in crossing_window_list:
         for crossing_threshold in crossing_threshold_list:
            for stop_loss in stop_loss_list:
               for rsi in rsi_list:
                  for purge in purge_list:
                     for sell_rsi in sell_rsi_list:
                        if rsi <= average_window + crossing_window and sell_rsi <= average_window + crossing_window:
                           bot = CrossingBot(average_window, crossing_window, crossing_threshold, stop_loss, rsi, purge, sell_rsi)
                           bot.trading_enabled = True
                           trader_list.append(bot)

   return trader_list


def simSingle():
   print("Simulating Single")
   trader = CrossingBot(9, 5, 0.2, 1.0, 4, 10, 12, simulation=True)
   simulate_single_trader(trader, "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SP500_10Min\\Tickers\\EPAM\\EPAM_2023-02-28_10 mins.csv")
   #trader = CrossingBot(12, 8, 0.3, 1.0, 4, 15, 8, simulation=True)
   #simulate_single_trader(trader, "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SP500_10Min\\Tickers\\META\\META_2023-02-28_10 mins.csv")


def simSP500():
   test_trader_list = build_trader_list("fast")

   ticker_dir = "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SP500_10Min\\"
   #ticker_file = "S&P500-Symbols.csv"
   ticker_file = "short_list.csv"

   simulate_ticker_group(test_trader_list, ticker_dir, ticker_file, top_traders=5)

if __name__ == "__main__":
   #simSP500()
   simSingle()