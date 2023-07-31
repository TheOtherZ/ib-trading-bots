from multiprocessing import Manager, Process
import os
import time

from ibapi.wrapper import BarData

from LiveCore.LiveTraderBase import LiveTraderBase

def forward_test(trader_cls, trader_config_list: list, tunning_period_bars, data_dir, ticker_file_name, top_traders=5, sav_file=None, top_to_test=50):
   best_traders = simulate_ticker_group(trader_cls, trader_config_list, data_dir, ticker_file_name, tunning_period_bars, top_traders, print_len=top_to_test)[:top_to_test]
   start_time = time.time()
   for trader in best_traders:
      trader.profit = 0
      ticker_bar_file_name = os.listdir(data_dir + "Tickers/" + trader.ticker)[0]
      ticker_bars = convert_bar_file(data_dir + "Tickers/" + trader.ticker + "/" + ticker_bar_file_name)[0]
      for bar in ticker_bars[tunning_period_bars:]:
         trader.process(bar, True)

   best_traders.sort(key=lambda x: x.profit, reverse=True)

   print("Completed forward test in %s" % (time.time() - start_time))
   for result in best_traders:
      print(f"{result.ticker} {result.get_stats()} {result.get_parameters()}")

   if sav_file is not None:
      with open(sav_file, 'w') as f:
            for result in best_traders:
               f.write(f"{result.ticker} {result.get_stats()} {result.get_parameters()}\n")

   

def simulate_ticker_group(trader_cls, trader_config_list: list, data_dir, ticker_file_name, num_bars_to_test=None, top_traders=5, sav_file=None, print_len=25, thread_limit=None):
   start_time = time.time()
   num_trader_sort = min(len(trader_config_list), top_traders)

   print("Testing with %s bots over %s " % (len(trader_config_list), ticker_file_name))
   results = []
   
   with Manager() as manager:
      result_queue = manager.Queue()
      thread_list = []
      with open(data_dir + ticker_file_name, "r") as ticker_f:
         for line in ticker_f:
            _, ticker = line.strip("\n").split(",")
            ticker_bar_file_name = os.listdir(data_dir + "Tickers/" + ticker)[0]
            ticker_bars = convert_bar_file(data_dir + "Tickers/" + ticker + "/" + ticker_bar_file_name)[0]
            if num_bars_to_test is not None:
               ticker_bars = ticker_bars[:num_bars_to_test]
            thread_list.append(Process(target=threaded_processor, args=(trader_cls, trader_config_list, result_queue, ticker_bars, ticker, num_trader_sort)))
            # if thread_limit is not None and len(thread_list) == thread_limit:
            #    for thread in thread_list:
            #       thread.start()
            #    for thread in thread_list:
            #       thread.join()

            #    while not result_queue.empty():
            #       results.append(result_queue.get())
            #    thread_list = []

      thread_idx = 0
      num_threads = len(thread_list)
      if thread_limit is None:
         thread_limit = num_threads
      while thread_idx < num_threads:
         end_idx = thread_idx + thread_limit if thread_idx + thread_limit < num_threads else num_threads
         for thread in thread_list[thread_idx:end_idx]:
            thread.start()
         for thread in thread_list[thread_idx:end_idx]:
            thread.join()
         thread_idx = end_idx
      
      while not result_queue.empty():
         results.append(result_queue.get())
   
   results.sort(key=lambda x: x.profit, reverse=True)

   print("Completed in %s" % (time.time() - start_time))
   if print_len is not None:
      for result in results[:print_len]:
         print(f"{result.ticker} {result.get_stats()} {result.get_parameters()}")

   if sav_file is not None:
      with open(sav_file, 'w') as f:
         if print_len is not None:
            for result in results[:print_len]:
               f.write(f"{result.ticker} {result.get_stats()} {result.get_parameters()}\n")
         else:
            for result in results:
               f.write(f"{result.ticker} {result.get_stats()} {result.get_parameters()}\n")
   
   return results

def threaded_processor(trader_cls, trader_config: list, result_queue, bar_data: list, ticker: str, num_results: int=5):
   trader_list = []
   for config in trader_config:
      trader_list.append(trader_cls(*config))
      trader_list[-1].trading_enabled = True
   for trader in trader_list:
      trader.ticker = ticker
      for bar in bar_data:
         trader.process(bar, True)

   trader_list.sort(key=lambda x: x.profit, reverse=True)
   for trader in trader_list[:num_results]:
      # result = (ticker, trader.profit, trader.drawdown, trader.num_trades, trader.total_costs, trader.compute_win_percent(), str(trader))
      result_queue.put(trader)

def simulate_bot_pool(trader_list: list[LiveTraderBase], data_dir):
   # get bar data
   bar_data = {}
   num_bars = 0
   for trader in trader_list:
      trader.trading_enabled = True
      ticker_bar_file_name = os.listdir(data_dir + "Tickers/" + trader.ticker)[0]
      ticker_bars = convert_bar_file(data_dir + "Tickers/" + trader.ticker + "/" + ticker_bar_file_name)[0]
      num_bars = len(ticker_bars)
      print(trader.ticker + " " + str(num_bars))
      bar_data[trader.ticker] = ticker_bars

   holding = None
   capital_used = 0
   for bar in range(num_bars):
      for trader in trader_list:
         if holding is not None and holding != trader.ticker:
            trader.trading_enabled = False
         elif holding is None:
            trader.trading_enabled = True

         trader.process(bar_data[trader.ticker][bar], True)

         if holding == trader.ticker and trader.num_held == 0:
            holding = None
         elif trader.num_held != 0:
            holding = trader.ticker
         
      if holding:
         capital_used += 1
   
   total_profit = 0
   for trader in trader_list:
      total_profit += trader.profit

   utilization = capital_used / num_bars * 100.0
   
   print(f"Total profit: {total_profit}, Capital utilization: {utilization}")

def compare_dates(ticker_1, ticker_2, data_dir):
   """ticker 1 should be longer"""
   ticker1_bar_file_name = os.listdir(data_dir + "Tickers/" + ticker_1)[0]
   ticker1_bars = convert_bar_file(data_dir + "Tickers/" + ticker_1 + "/" + ticker1_bar_file_name)[0]
   ticker2_bar_file_name = os.listdir(data_dir + "Tickers/" + ticker_2)[0]
   ticker2_bars = convert_bar_file(data_dir + "Tickers/" + ticker_2 + "/" + ticker2_bar_file_name)[0]
   for x in range(len(ticker1_bars)):
      if ticker1_bars[x].date != ticker2_bars[x].date:
         print(f"{ticker_1} {ticker1_bars[x].date} != {ticker_2} {ticker2_bars[x].date}")
         break


def make_bar(date, open, high, low, close, volume, average, barCount):
   new_bar = BarData()
   new_bar.date = str(date)
   new_bar.open = float(open)
   new_bar.high = float(high)
   new_bar.low = float(low)
   new_bar.close = float(close)
   new_bar.volume = int(float(volume))
   new_bar.wap = float(average)
   new_bar.barCount = int(barCount)

   return new_bar

def convert_bar_file(bar_file_name: str):
   bars = []
   period_size = 0
   with open(bar_file_name, 'r') as bar_file:
      # Strip off column headers
      period_size = len(list(bar_file.readline().split(",")))
      for line in bar_file.readlines():
         bars.append(make_bar(*list(line.split(","))))
   
   return bars, period_size