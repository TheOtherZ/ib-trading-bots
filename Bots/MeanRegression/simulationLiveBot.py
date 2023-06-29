from LiveCore.Simulator import simulate_ticker_group, simulate_bot_pool, compare_dates, forward_test
from MeanRegressionBotLive import MeanRegressionBotLive

def build_config_list(frame="fast") -> list:
   config_list = []

   # average_window, crossing_window, crossing_threshold, stop_loss, rsi_window, profit_horizon, profit_take
   if frame == "fast":
      average_window_list = [280, 120]
      crossing_window_long_list = [40, 60, 80]
      crossing_window_list = [10, 16, 24]
      stop_loss_list = [2.0]
      rsi_list = [8]
      profit_take_list = [3.0, 4.0, 5.0]
   elif frame == "medium":
      average_window_list = [60, 80, 120]
      crossing_window_long_list = [40, 60, 80]
      crossing_window_list = [8, 10]
      stop_loss_list = [2.0, 3.0]
      rsi_list = [8]
      profit_take_list = [3.0, 4.0, 5.0]
   elif frame == "long":
      average_window_list = [60, 80, 120, 150, 200]
      crossing_window_long_list = [40, 60, 80, 120]
      crossing_window_list = [10, 16, 24, 40, 60]
      stop_loss_list = [2.0, 3.0, 4.0]
      rsi_list = [8]
      profit_take_list = [2.0, 3.0, 4.0, 5.0]

   
   for average_window in average_window_list:
      for long_crossing in crossing_window_long_list:
         for crossing_window in crossing_window_list:
            for stop_loss in stop_loss_list:
               for rsi in rsi_list:
                  for profit in profit_take_list:
                     if long_crossing > crossing_window:
                        config_list.append([average_window, long_crossing, crossing_window, stop_loss, rsi, profit, "TEST"])

   return config_list


def simSp500(log_name):
   test_trader_config = build_config_list("long")

   ticker_dir = "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SP500_10Min\\"
   ticker_file = "S&P500-Symbols.csv"
   #ticker_file = "quick-list-mean-conversion-live.csv"
   #ticker_file = "etf-symbols.csv"

   simulate_ticker_group(MeanRegressionBotLive, test_trader_config, ticker_dir, ticker_file, top_traders=5, sav_file=log_name, print_len=None, thread_limit=None)

def simSp50030Min():
   test_trader_list = build_config_list("fast")

   ticker_dir = "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SP500_30Min\\"
   ticker_file = "S&P500-Symbols.csv"
   #ticker_file = "quick-list-mean-conversion.csv"
   #ticker_file = "etf-symbols.csv"

   simulate_ticker_group(test_trader_list, ticker_dir, ticker_file, top_traders=5, sav_file="sp500-30min.txt", print_len=None)

def simSp500OneBot():
   test_trader_config = [[120, 80, 10, 2.0, 8, 3.0, "TEST"]]

   ticker_dir = "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SP500_10Min\\"
   #ticker_file = "S&P500-Symbols.csv"
   ticker_file = "quick-list-mean-conversion-live.csv"
   #ticker_file = "quick-list-mean-conversion.csv"
   #ticker_file = "etf-symbols.csv"

   simulate_ticker_group(MeanRegressionBotLive, test_trader_config, ticker_dir, ticker_file, top_traders=1, sav_file="sp500-single-bot-short-list.txt", print_len=None)

def forward_test_sp_500():
   test_trader_list = build_config_list("medium")
   ticker_dir = "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SPY_10Min_Bars_Long\\"
   ticker_file = "ticker_list.csv"
   tunning_period = 19554
   forward_test(MeanRegressionBotLive, test_trader_list, tunning_period, ticker_dir, ticker_file, 10, "Index_Forward_Test.txt" )

def reduce_results(file_name, out_name, win_rate):
   with open(file_name, 'r') as src:
      with open(out_name, 'w') as dest:
         tickers = []
         for line in src:
            data = line.split(" ")
            ticker = data[0]
            winning = float(data[3].strip(','))
            if ticker not in tickers and winning >= win_rate:
               tickers.append(ticker)
               dest.write(line)

def convert_to_prototypes(file_name, out_name, capital=10000):
   import re
   regex = re.compile("\(([^\)]+)\)")
   with open(file_name, 'r') as src:
      with open(out_name, 'w') as dest:
         for line in src:
            ticker = line.split(" ")[0]
            results = regex.findall(line)
            params = results[1]
            prototype = 'MeanRegressionBotLive(' + params + ', "' + ticker + '", ' + str(capital) + ', simulation=False, name="'+ ticker + 'RegressionBot"),# ' + results[0] + '\n'
            dest.write(prototype)

def simBotPool():
   ticker_dir = "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\Recent_10_min\\"
   bot_pool = [
      #MeanRegressionBotLive(120, 80, 10, 2.0, 8, 5.0, "WBD"),
      MeanRegressionBotLive(120, 80, 10, 2.0, 8, 5.0, "NVDA"),
      MeanRegressionBotLive(120, 80, 10, 2.0, 8, 5.0, "ETSY"),
      MeanRegressionBotLive(120, 80, 16, 2.0, 8, 3.0, "PYPL"),
      MeanRegressionBotLive(80, 60, 10, 2.0, 8, 4.0, "TSLA"),
      MeanRegressionBotLive(80, 60, 10, 2.0, 8, 3.0, "META"),
      MeanRegressionBotLive(120, 80, 10, 2.0, 8, 5.0, "CZR"),
      MeanRegressionBotLive(120, 80, 10, 2.0, 8, 4.0, "STLD"),
      MeanRegressionBotLive(120, 80, 10, 2.0, 8, 3.0, "NXPI"),
      MeanRegressionBotLive(120, 80, 10, 2.0, 8, 4.0, "SPGI"),
      MeanRegressionBotLive(120, 80, 10, 2.0, 8, 5.0, "CHRW"),
      MeanRegressionBotLive(60, 80, 10, 2.0, 8, 3.0, "UAL"),
      MeanRegressionBotLive(120, 80, 10, 2.0, 8, 3.0, "PWR"),
      MeanRegressionBotLive(120, 80, 10, 2.0, 8, 4.0, "DVA"),
      MeanRegressionBotLive(80, 60, 10, 2.0, 8, 3.0, "BBWI"),
   ]

   simulate_bot_pool(bot_pool, ticker_dir)


if __name__ == "__main__":
   name = "no-rsi-9-all-500.txt"
   #simSp500(name)
   #simSp500OneBot()
   reduce_results(name, "reduced-win-rate-" + name, 0.65)
   convert_to_prototypes("reduced-win-rate-" + name, "prototypes-" + name, 5000)
