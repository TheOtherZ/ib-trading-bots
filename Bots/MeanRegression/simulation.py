from Simulation.Simulator import simulate_single_source, simulate_ticker_group, simulate_single_bar_file, simulate_single_trader
from MeanRegressionBot import MeanRegressionBot

def build_trader_list(frame="fast") -> list[MeanRegressionBot]:
   trader_list = []

   # average_window, crossing_window, crossing_threshold, stop_loss, rsi_window, profit_horizon, profit_take
   if frame == "fast":
      average_window_list = [20, 30, 40, 60]
      crossing_window_list = [10, 16, 24]
      stop_loss_list = [2.0, 3.0]
      rsi_list = [8, 12]
      profit_window_list = [4, 8, 12]
   elif frame == "medium":
      average_window_list = [20, 30, 40, 60, 80]
      crossing_window_list = [10, 16, 24, 40]
      stop_loss_list = [1.0, 2.0, 3.0]
      rsi_list = [8, 12]
      profit_window_list = [4, 8, 12]
   elif frame == "long":
      average_window_list = [20, 30, 40, 60, 80, 120, 150]
      crossing_window_list = [10, 16, 24, 40, 60, 80, 100, 120]
      stop_loss_list = [0.5, 1.0, 2.0, 3.0, 4.0]
      rsi_list = [4, 8, 12, 20, 35]
      profit_window_list = [4, 8, 12]

   
   for average_window in average_window_list:
      for crossing_window in crossing_window_list:
         for stop_loss in stop_loss_list:
            for rsi in rsi_list:
               for profit_window in profit_window_list:
                  bot = MeanRegressionBot(average_window, crossing_window, stop_loss, rsi, profit_window, "TEST")
                  bot.trading_enabled = True
                  trader_list.append(bot)

   return trader_list

def proof_of_concept():
   test_trader_list = build_trader_list("fast")

   ticker_dir = "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SP500_10Min\\"
   ticker_file = "S&P500-Symbols.csv"
   #ticker_file = "quick-list.csv"
   #ticker_file = "etf-symbols.csv"

   simulate_ticker_group(test_trader_list, ticker_dir, ticker_file, top_traders=5, sav_file="sp500-window.txt", print_len=None)


if __name__ == "__main__":
   proof_of_concept()