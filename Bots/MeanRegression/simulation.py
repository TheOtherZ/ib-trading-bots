from Simulation.Simulator import simulate_single_source, simulate_ticker_group, simulate_single_bar_file, simulate_single_trader
from MeanRegressionBot import MeanRegressionBot

def build_trader_list(frame="fast") -> list[MeanRegressionBot]:
   trader_list = []

   # average_window, crossing_window, crossing_threshold, stop_loss, rsi_window, profit_horizon, profit_take
   if frame == "fast":
      average_window_list = [20, 60, 120]
      crossing_window_list = [10, 16, 24]
      stop_loss_list = [2.0]
      rsi_list = [8]
      profit_take_list = [3.0, 4.0, 5.0]
   elif frame == "medium":
      average_window_list = [20, 30, 40, 60, 80]
      crossing_window_list = [10, 16, 24, 40]
      stop_loss_list = [2.0]
      rsi_list = [8, 12]
      profit_take_list = [2.0, 3.0, 4.0, 5.0]
   elif frame == "long":
      average_window_list = [20, 40, 80, 120, 150]
      crossing_window_list = [10, 16, 24, 40, 60]
      stop_loss_list = [0.5, 1.0, 2.0, 3.0, 4.0]
      rsi_list = [8, 12, 20]
      profit_take_list = [2.0, 3.0, 4.0, 5.0]

   
   for average_window in average_window_list:
      for crossing_window in crossing_window_list:
         for stop_loss in stop_loss_list:
            for rsi in rsi_list:
               for profit in profit_take_list:
                  bot = MeanRegressionBot(average_window, crossing_window, stop_loss, rsi, profit, "TEST")
                  bot.trading_enabled = True
                  trader_list.append(bot)

   return trader_list

def proof_of_concept():
   test_trader_list = []
   test_trader_list.append(MeanRegressionBot(20, 10, 4.0, 12, 2.0))
   test_trader_list.append(MeanRegressionBot(20, 10, 4.0, 12, 2.0))

   ticker_dir = "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SP500_10Min\\"
   ticker_file = "S&P500-Symbols.csv"
   #ticker_file = "quick-list-mean-conversion.csv"
   #ticker_file = "etf-symbols.csv"

   simulate_ticker_group(test_trader_list, ticker_dir, ticker_file, top_traders=5, sav_file="sp500-fixed-stop-loss.txt", print_len=None)

def simSp500():
   test_trader_list = build_trader_list("medium")

   ticker_dir = "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SP500_10Min\\"
   #ticker_file = "S&P500-Symbols.csv"
   #ticker_file = "quick-list-mean-conversion.csv"
   ticker_file = "etf-symbols.csv"

   simulate_ticker_group(test_trader_list, ticker_dir, ticker_file, top_traders=5, sav_file="sp500-old-sim-exit.txt", print_len=None)

def simSp50030Min():
   test_trader_list = build_trader_list("fast")

   ticker_dir = "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SP500_30Min\\"
   ticker_file = "S&P500-Symbols.csv"
   #ticker_file = "quick-list-mean-conversion.csv"
   #ticker_file = "etf-symbols.csv"

   simulate_ticker_group(test_trader_list, ticker_dir, ticker_file, top_traders=5, sav_file="sp500-30min.txt", print_len=None)


if __name__ == "__main__":
   simSp500()