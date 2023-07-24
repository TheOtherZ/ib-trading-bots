from LiveCore.Simulator import simulate_ticker_group, simulate_bot_pool, forward_test

from TrendBot import TrendBot

def build_config_list(frame="fast") -> list:
   config_list = []

   # jump_threshold_percent: float, average_velocity_window: int, quick_velocity_window: int, stop_loss: float, profit_take: float
   if frame == "fast":
      jump_threshold_percent_list = [1.0, 2.0, 3.0]
      average_velocity_window_list = [40, 60, 80]
      quick_velocity_window_list = [10, 16, 24]
      stop_loss_list = [2.0]
      profit_take_list = [1.0, 2.0]
   elif frame == "long":
      jump_threshold_percent_list = [1.0, 2.0, 3.0, 4.0]
      average_velocity_window_list = [40, 60, 80, 120, 200]
      quick_velocity_window_list = [10, 16, 24, 36]
      stop_loss_list = [1.0, 2.0, 3.0]
      profit_take_list = [1.0, 2.0, 3.0]
   else:
      jump_threshold_percent_list = [1.0]
      average_velocity_window_list = [40, 60, 80]
      quick_velocity_window_list = [10, 16, 24]
      stop_loss_list = [2.0]
      profit_take_list = [1.0]

   
   for jump_threshold_percent in jump_threshold_percent_list:
      for average_velocity_window in average_velocity_window_list:
         for quick_velocity_window in quick_velocity_window_list:
            for stop_loss in stop_loss_list:
               for profit_take in profit_take_list:
                  config_list.append([jump_threshold_percent, average_velocity_window, quick_velocity_window, stop_loss,profit_take, "TEST"])
   
   return config_list

def simSp500(log_name):
   test_trader_config = build_config_list("long")

   ticker_dir = "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SP500_10Min\\"
   #ticker_file = "S&P500-Symbols.csv"
   ticker_file = "short-list-crossing-trend.csv"
   #ticker_file = "etf-symbols.csv"

   simulate_ticker_group(TrendBot, test_trader_config, ticker_dir, ticker_file, top_traders=5, sav_file=log_name, print_len=None, thread_limit=8)

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

def convert_to_prototypes(file_name, out_name, capital=5000):
   import re
   regex = re.compile("\(([^\)]+)\)")
   with open(file_name, 'r') as src:
      with open(out_name, 'w') as dest:
         for line in src:
            ticker = line.split(" ")[0]
            results = regex.findall(line)
            params = results[1]
            prototype = 'TrendBot(' + params + ', "' + ticker + '", ' + "capital=" + str(capital) + ', simulation=False, name="'+ ticker + 'TrendBot"),# ' + results[0] + '\n'
            dest.write(prototype)

if __name__ == "__main__":
   log_name = "POC-500.txt"
   #simSp500(log_name)
   #reduce_results(log_name, "reduced-" + log_name, 0.7)
   convert_to_prototypes("reduced-" + log_name, "prototypes-" + log_name)