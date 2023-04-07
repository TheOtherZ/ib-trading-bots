from copy import deepcopy
from multiprocessing import Process, Manager, JoinableQueue
from queue import PriorityQueue
import time
import os

from TraderCore.TraderBase import TraderBase
from Simulation.FileProcessing import make_flat_bars_from_master, convert_bar_file

def process_single_source(traders: list[TraderBase], return_vals, start_idx, flat_data, day_period=None):
   bar_num = 0
   for trader in traders:
      for bar in flat_data:
         trader.process(bar)
         bar_num += 1
         if day_period is not None and bar_num % day_period == 0:
            trader.reset(True)

   x = start_idx
   for bot in traders: 
      return_vals[x] = bot
      x += 1

def threaded_processor(traders: list[TraderBase], result_queue, bar_data: list, ticker: str, num_results: int=5):
   for trader in traders:
      trader.ticker = ticker
      for bar in bar_data:
         trader.process(bar)

   traders.sort(reverse=True)
   for trader in traders[:num_results]:
      result = (ticker, trader.profit, trader.drawdown, trader.num_trades, trader.total_costs, trader.compute_win_percent(), str(trader))
      result_queue.put(result)
      #result_queue.task_done()

   # result_queue.close()

def process_dual_source(traders: list[TraderBase], return_vals, start_idx, flat_data1, flat_data2, day_period=None):
   bar_num = 0
   for trader in traders:
      for (bar1, bar2) in zip(flat_data1, flat_data2):
         trader.process(bar1, bar2)
         bar_num += 1
         if day_period is not None and bar_num % day_period == 0:
            trader.reset(True)

   x = start_idx
   for bot in traders: 
      return_vals[x] = bot
      x += 1

def simulate_single_trader(trader: TraderBase, bar_data_file, print_stats=True):
   trader.trading_enabled = True
   bars = convert_bar_file(bar_data_file)[0]
   for bar in bars:
      trader.process(bar)

   if print_stats:
      trader.print_stats()
      print(trader)

def simulate_ticker_group(traders: list[TraderBase], data_dir, ticker_file_name, day_period=None, top_traders=5, sav_file=None, print_len=25, sort_win_rate=False):
   start_time = time.time()
   num_trader_sort = min(len(traders), top_traders)

   #result_queue = JoinableQueue()

   print("Testing with %s bots over %s " % (len(traders), ticker_file_name))
   results = []
   
   with Manager() as manager:
      result_queue = manager.Queue()
      thread_list = []
      with open(data_dir + ticker_file_name, "r") as ticker_f:
         for line in ticker_f:
            _, ticker = line.strip("\n").split(",")
            ticker_bar_file_name = os.listdir(data_dir + "Tickers/" + ticker)[0]
            ticker_bars = convert_bar_file(data_dir + "Tickers/" + ticker + "/" + ticker_bar_file_name)[0]
            trader_list_copy = []
            for trader in traders:
               trader_list_copy.append(deepcopy(trader))
            thread_list.append(Process(target=threaded_processor, args=(trader_list_copy, result_queue, ticker_bars, ticker, num_trader_sort)))
            thread_list[-1].start()

      #result_queue.join()

      for thread in thread_list:
         thread.join()

      while not result_queue.empty():
         results.append(result_queue.get())

   if sort_win_rate:
      sort_idx = 5
   else:
      sort_idx = 1
   
   results.sort(key=lambda x: x[sort_idx], reverse=True)

   print("Completed in %s" % (time.time() - start_time))
   for result in results[:25]:
      print(result)

   if sav_file is not None:
      with open(sav_file, 'w') as f:
         if print_len is not None:
            for result in results[:print_len]:
               f.write(str(result) +"\n")
         else:
            for result in results:
               f.write(str(result) +"\n")

def simulate_single_bar_file(traders, bar_file_name, threads):
   start_time = time.time()

   ticker_bars = convert_bar_file(bar_file_name)[0]
   print("Testing with %s bots over %s bars" % (len(traders), len(ticker_bars)))

   manager = Manager()
   managed_traders = manager.list(traders)

   if threads == 1:
      process_single_source(traders, managed_traders, 0, ticker_bars)
   elif threads > 1:
      subdivide = int(len(traders) / threads)
      end = subdivide
      start = 0
      thread_list = [None] * threads
      for x in range(threads):
         if x == threads - 1:
            end = len(traders)
         thread_list[x] = Process(target=process_single_source, args=(traders[start:end], managed_traders, start, ticker_bars))
         thread_list[x].start()
         start = end
         end += subdivide

      for thread in thread_list:
         thread.join()

   print("Completed in %s" % (time.time() - start_time))
   managed_traders.sort(reverse=True)
   #managed_traders.sort(key=lambda x: x.profit, reverse=True)
   for trader in managed_traders[:5]:
      trader.print_stats()
      print(trader)

def simulate_single_source(traders: list[TraderBase], data_dir, master_data_file_name, day_period=None, threads=1):
   start_time = time.time()

   flat_data = make_flat_bars_from_master(master_data_file_name, data_dir)[10074:]#TODO
   print("Testing with %s bots over %s bars single source" % (len(traders), len(flat_data)))

   manager = Manager()
   managed_traders = manager.list(traders)

   if threads == 1:
      process_single_source(traders, managed_traders, 0, flat_data)
   elif threads > 1:
      subdivide = int(len(traders) / threads)
      end = subdivide
      start = 0
      thread_list = [None] * threads
      for x in range(threads):
         if x == threads - 1:
            end = len(traders)
         thread_list[x] = Process(target=process_single_source, args=(traders[start:end], managed_traders, start, flat_data))
         thread_list[x].start()
         start = end
         end += subdivide

      for thread in thread_list:
         thread.join()

   print("Completed in %s" % (time.time() - start_time))
   managed_traders.sort(reverse=True)
   #managed_traders.sort(key=lambda x: x.profit, reverse=True)
   for trader in managed_traders[:5]:
      trader.print_stats()
      print(trader)

def simulate_dual_source(traders: list[TraderBase], data_dir1, master_data_file_name1, data_dir2, master_data_file_name2, day_period=None, threads=1):
   start_time = time.time()

   flat_data1 = make_flat_bars_from_master(master_data_file_name1, data_dir1)
   flat_data2 = make_flat_bars_from_master(master_data_file_name2, data_dir2)
   print("Testing with %s bots over %s bars dual source" % (len(traders), len(flat_data1)))

   manager = Manager()
   managed_traders = manager.list(traders)

   if threads == 1:
      process_dual_source(traders, managed_traders, 0, flat_data1, flat_data2)
   elif threads > 1:
      subdivide = int(len(traders) / threads)
      end = subdivide
      start = 0
      thread_list = [None] * threads
      for x in range(threads):
         if x == threads - 1:
            end = len(traders)
         thread_list[x] = Process(target=process_dual_source, args=(traders[start:end], managed_traders, start, flat_data1, flat_data2))
         thread_list[x].start()
         start = end
         end += subdivide

      for thread in thread_list:
         thread.join()

   print("Completed in %s" % (time.time() - start_time))
   managed_traders.sort(reverse=True)
   #managed_traders.sort(key=lambda x: x.profit, reverse=True)
   for trader in managed_traders[:5]:
      trader.print_stats()
      print(trader)

def worker(traders: list[TraderBase], result_queue: JoinableQueue, bar_data: list, ticker: str, num_results: int=5):
   for trader in traders:
      trader.ticker = ticker
      for bar in bar_data:
         trader.process(bar)

   traders.sort(reverse=True)
   for trader in traders[:num_results]:
      result = (ticker, trader.profit, trader.drawdown, trader.num_trades, trader.total_costs, str(trader))
      result_queue.put(result)
      result_queue.task_done()

if __name__ == "__main__":
   test_trader_list = [TraderBase(), TraderBase()]

   ticker_dir = "/home/zimbra/development/IBBot/Data/SP500_10Min/"
   ticker_file = "S&P500-Symbols.csv"

   simulate_ticker_group(test_trader_list, ticker_dir, ticker_file, threads=8)