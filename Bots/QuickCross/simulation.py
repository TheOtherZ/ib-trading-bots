from Simulation.Simulator import simulate_single_source, simulate_ticker_group, simulate_single_bar_file, simulate_single_trader
from QuickCross import QuickCross

def build_trader_list(frame=None, strange=False) -> list[QuickCross]:
   trader_list = []

   # average_window, crossing_window, crossing_threshold, stop_loss, rsi_window, profit_horizon, profit_take
   if frame == "full":
      average_window_list = [20, 30, 40]
      crossing_window_list = [8, 10, 16]
      crossing_threshold_list = [.2, .3, 0.4]
      stop_loss_list = [1.0]
      rsi_list = [4, 8, 12]
      profit_horizon_list = [5, 8]
      profit_take_list = [0.2, 0.3, 0.5]
   elif frame == "fast":
      average_window_list = [12, 20]
      crossing_window_list = [5, 8, 10]
      crossing_threshold_list = [.1, .2, .3]
      stop_loss_list = [1.0]
      rsi_list = [4, 8, 12]
      profit_horizon_list = [5, 8]
      profit_take_list = [0.2, 0.3, 0.5]
   else:
      average_window_list = [9, 12, 20]
      crossing_window_list = [5, 8, 10]
      crossing_threshold_list = [.1, .2, .3]
      stop_loss_list = [1.0, 1.5]
      rsi_list = [4, 8, 12]
      profit_horizon_list = [3, 5, 8]
      profit_take_list = [0.2, 0.3, 0.5, 0.7]

   for average_window in average_window_list:
      for crossing_window in crossing_window_list:
         for crossing_threshold in crossing_threshold_list:
            for stop_loss in stop_loss_list:
               for rsi in rsi_list:
                  for profit_horizon in profit_horizon_list:
                     for profit_take in profit_take_list:
                        if rsi <= average_window + crossing_window:
                           bot = QuickCross(average_window, crossing_window, crossing_threshold, stop_loss, rsi, profit_horizon, profit_take)
                           bot.trading_enabled = True
                           trader_list.append(bot)

   return trader_list

def simSP500():
   test_trader_list = build_trader_list("full")

   ticker_dir = "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SP500_10Min\\"
   #ticker_file = "S&P500-Symbols.csv"
   ticker_file = "quick-list.csv"

   simulate_ticker_group(test_trader_list, ticker_dir, ticker_file, top_traders=5, sav_file="qick-list-relaxed-stochastic.txt", print_len=None)

if __name__ == "__main__":
   simSP500()