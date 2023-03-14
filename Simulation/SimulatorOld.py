from lib2to3.pygram import pattern_symbols
from multiprocessing import Process, Manager
import time

from IBTradingBot import TradingCosts
from MicroTrader import MicroTraderBot
from VolumeTrader import VolumeTraderBot
from MomentumCrossingTrader import MomentumCrossingBot
from MomentumTrader import MomentumTraderBot

import HelperFunctions as hf

def test_with_file_thread(trader_list, file_list, return_traders, start_idx, evening_closeout_ticks=800):
   for triple_files in reversed(file_list):
      underlying_file = triple_files[0]
      short_file = triple_files[1]
      long_file = triple_files[2]

      with open(underlying_file, 'r') as u_file:
         with open(short_file, 'r') as s_file:
            with open(long_file, 'r') as l_file:
               # Strip off column headers
               u_line = u_file.readline()
               s_line = s_file.readline()
               l_line = l_file.readline()

               data_count = 0
               for u_line in u_file.readlines():
                  s_line = s_file.readline()
                  l_line = l_file.readline()

                  u_bar = hf.make_bar(*list(u_line.split(",")))
                  s_bar = hf.make_bar(*list(s_line.split(",")))
                  l_bar = hf.make_bar(*list(l_line.split(",")))
                  if data_count == 0:
                     for bot in trader_list:
                        bot.compute_share_quantities(s_bar.close, l_bar.close)
                  data_count += 1

                  if data_count >= evening_closeout_ticks:
                     for bot in trader_list:
                        bot.disable_buying()

                  for bot in trader_list:
                     bot.on_bar_update(u_bar, s_bar, l_bar)

      for bot in trader_list:
         bot.close_all_positions(s_bar.close, l_bar.close)
         bot.start_new_trading_period()

   x = start_idx
   for bot in trader_list: 
      return_traders[x] = bot
      x += 1

def multithreaded_runner(trader_list, master_file_list, evening_closeout_ticks=800, num_threads=4):
   manager = Manager()
   subdivide = int(len(trader_list) / num_threads)
   end = subdivide
   start = 0
   thread_list = [None] * num_threads
   result_list = manager.list(trader_list)
   for x in range(num_threads):
      if x == num_threads - 1:
         end = len(trader_list)
      thread_list[x] = Process(target=test_with_file_thread, args=(trader_list[start:end], master_file_list, result_list, start, evening_closeout_ticks))
      thread_list[x].start()
      start = end
      end += subdivide

   for x in range(num_threads):
      thread_list[x].join()

   final_return_list = []
   for trader in result_list:
      final_return_list.append(trader)
   
   return final_return_list

def snowball_backtest(starting_capital=20000, evening_disable_ticks=800) -> MomentumCrossingBot:
   file_list = "Data2/historic_data_list.txt"

   master_file_list = hf.create_master_file_list(file_list)
   # for item in master_file_list: Sanity check
   #    print(item)
   trading_costs = TradingCosts(0.02, 0.005, 0.0000229, 0.00013, 1.00)
   trader = MomentumCrossingBot(3.5, 30, 120, 0.5, 35, 15, 50, trading_costs, starting_capital)
   #trader = MomentumCrossingBot(2.5, 60, 80, 0.3, 28, 25, 25, trading_costs, 20000)

   end_day_holding = 0
   print("Snowball test over %s days" % len(master_file_list))

   last_day_profit = 0
   for item in master_file_list:
      with open(item[0], 'r') as u_file:
            with open(item[1], 'r') as s_file:
               with open(item[2], 'r') as l_file:
                  # Strip off column headers
                  u_line = u_file.readline()
                  s_line = s_file.readline()
                  l_line = l_file.readline()

                  data_count = 0
                  for u_line in u_file.readlines():
                     s_line = s_file.readline()
                     l_line = l_file.readline()

                     u_bar = hf.make_bar(*list(u_line.split(",")))
                     s_bar = hf.make_bar(*list(s_line.split(",")))
                     l_bar = hf.make_bar(*list(l_line.split(",")))
                     if data_count == 0:
                        trader.compute_share_quantities(s_bar.close, l_bar.close)
                     data_count += 1

                     if data_count >= evening_disable_ticks:
                        trader.disable_buying()

                     trader.on_bar_update(u_bar, s_bar, l_bar)
      if trader.holding:
         end_day_holding += 1
      trader.close_all_positions(s_bar.close, l_bar.close)
      if trader.day_profit:
         trader.capital += trader.day_profit
      trader.start_new_trading_period()
   

   trader.print_stats()
   trader.print_configuration()
   print("Closed %s positions at end of day" % end_day_holding)

   return trader

def snowball_backtest_1min(file_list="Data1Min2/historic_data_list.txt", starting_capital=20000, evening_disable_ticks=800) -> MomentumCrossingBot:
   master_file_list = hf.create_master_file_list(file_list)
   # for item in master_file_list: Sanity check
   #    print(item)
   trading_costs = TradingCosts(0.02, 0.005, 0.0000229, 0.00013, 1.00)
   trader = MomentumCrossingBot(2.5, 15, 40, 0.6, 14, 15, 50, trading_costs, starting_capital)

   end_day_holding = 0
   print("Snowball test over %s days" % len(master_file_list))

   last_day_profit = 0
   for item in reversed(master_file_list):
      with open(item[0], 'r') as u_file:
            with open(item[1], 'r') as s_file:
               with open(item[2], 'r') as l_file:
                  # Strip off column headers
                  u_line = u_file.readline()
                  s_line = s_file.readline()
                  l_line = l_file.readline()

                  data_count = 0
                  for u_line in u_file.readlines():
                     s_line = s_file.readline()
                     l_line = l_file.readline()

                     u_bar = hf.make_bar(*list(u_line.split(",")))
                     s_bar = hf.make_bar(*list(s_line.split(",")))
                     l_bar = hf.make_bar(*list(l_line.split(",")))
                     if data_count == 0:
                        trader.compute_share_quantities(s_bar.close, l_bar.close)
                     data_count += 1

                     if data_count >= evening_disable_ticks:
                        trader.disable_buying()

                     trader.on_bar_update(u_bar, s_bar, l_bar)
      if trader.holding:
         end_day_holding += 1
      trader.close_all_positions(s_bar.close, l_bar.close)
      # if trader.day_profit:
      #    trader.capital += trader.day_profit
      trader.start_new_trading_period()
   

   trader.print_stats()
   trader.print_configuration()
   print("Closed %s positions at end of day" % end_day_holding)

   return trader



def adaptive_backtest_1min(file_list="Data1Min2/historic_data_list.txt", starting_capital=20000, evening_disable_ticks=800) -> MomentumCrossingBot:
   master_file_list = hf.create_master_file_list(file_list)
   # for item in master_file_list: Sanity check
   #    print(item)
   trading_costs = TradingCosts(0.02, 0.005, 0.0000229, 0.00013, 1.00)
   trader = MomentumCrossingBot(2.5, 50, 80, 0.5, 28, 20, 50, trading_costs, starting_capital)

   end_day_holding = 0
   print("Snowball test over %s days" % len(master_file_list))

   past_30 = []
   for item in reversed(master_file_list):
      with open(item[0], 'r') as u_file:
            with open(item[1], 'r') as s_file:
               with open(item[2], 'r') as l_file:
                  # Strip off column headers
                  u_line = u_file.readline()
                  s_line = s_file.readline()
                  l_line = l_file.readline()

                  data_count = 0
                  for u_line in u_file.readlines():
                     s_line = s_file.readline()
                     l_line = l_file.readline()

                     u_bar = hf.make_bar(*list(u_line.split(",")))
                     s_bar = hf.make_bar(*list(s_line.split(",")))
                     l_bar = hf.make_bar(*list(l_line.split(",")))
                     if data_count == 0:
                        trader.compute_share_quantities(s_bar.close, l_bar.close)
                     data_count += 1

                     if data_count >= evening_disable_ticks:
                        trader.disable_buying()

                     trader.on_bar_update(u_bar, s_bar, l_bar)
      if trader.holding:
         end_day_holding += 1
      trader.close_all_positions(s_bar.close, l_bar.close)
      # if trader.day_profit:
      #    trader.capital += trader.day_profit
      trader.start_new_trading_period()

      past_30.append(item)
      if len(past_30) % 30 == 0:
         args = back_test_crossing_bot_params(past_30, trading_costs)
         trader.set_parameters(*args)
         past_30 = []
         
   

   trader.print_stats()
   trader.print_configuration()
   print("Closed %s positions at end of day" % end_day_holding)

   return trader


def back_test_crossing_bot_params(file_list, trading_costs):

   stop_loss_list = [2.5, 3.5]
   moving_average_list = [30, 40, 50]
   crossing_count_list = [80, 120, 160]
   crossing_signal_list = [0.4, 0.5, 0.6]
   rsi_period_list = [28, 35, 45]
   rsi_threshold_list = [15, 20, 30]
   rsi_buy_list = [40, 50]

   start_time = time.time()

   trader_list = []
   for stop_loss in stop_loss_list:
      for moving_avg in moving_average_list:
         for crossing_count in crossing_count_list:
            for crossing_signal in crossing_signal_list:
               for rsi_period in rsi_period_list:
                  for rsi_threshold in rsi_threshold_list:
                     for rsi_buy in rsi_buy_list:
                        trader_list.append(MomentumCrossingBot(stop_loss, moving_avg, crossing_count, crossing_signal, rsi_period, rsi_threshold, rsi_buy, trading_costs, 10000, 200))

   results = multithreaded_runner(trader_list, file_list, 800, 8)

   results.sort(key=lambda x: x.profit, reverse=True)
   results[0].print_configuration()
   return (results[0].stop_loss_percent, results[0].moving_average_window, results[0].crossing_window, results[0].crossing_threshold, results[0].rsi_period, results[0].rsi_signal, results[0].rsi_open)

def back_test_crossing_bot():
   file_list = "Data2/historic_data_list.txt"

   master_file_list = hf.create_master_file_list(file_list)
   # for item in master_file_list: Sanity check
   #    print(item)
   trading_costs = TradingCosts(0.02, 0.005, 0.0000229, 0.00013, 1.00)

   # This takes a long time
   # stop_loss_list = [1.0, 2.5, 3.5, 4.0]
   # moving_average_list = [50, 60, 80, 120]
   # crossing_count_list = [80, 120, 140, 160]
   # crossing_signal_list = [0.25, 0.3, 0.35, 0.45]
   # rsi_period_list = [14, 28, 40]
   # rsi_threshold_list = [10, 15, 25]
   # rsi_buy_list = [40, 50, 60]

   stop_loss_list = [2.5, 3.5]
   moving_average_list = [30, 40, 50]
   crossing_count_list = [80, 120, 160]
   crossing_signal_list = [0.4, 0.5, 0.6]
   rsi_period_list = [28, 35, 45]
   rsi_threshold_list = [15, 20, 30]
   rsi_buy_list = [40, 50]

   start_time = time.time()

   trader_list = []
   for stop_loss in stop_loss_list:
      for moving_avg in moving_average_list:
         for crossing_count in crossing_count_list:
            for crossing_signal in crossing_signal_list:
               for rsi_period in rsi_period_list:
                  for rsi_threshold in rsi_threshold_list:
                     for rsi_buy in rsi_buy_list:
                        trader_list.append(MomentumCrossingBot(stop_loss, moving_avg, crossing_count, crossing_signal, rsi_period, rsi_threshold, rsi_buy, trading_costs, 10000, 200))

   print("Testing Momentum Crossing with %s bots over %s days" % (len(trader_list), len(master_file_list)))
   results = multithreaded_runner(trader_list, master_file_list, 800, 8)

   print("Completed in %s" % (time.time() - start_time))
   results.sort(key=lambda x: x.profit, reverse=True)
   for trader in results[:6]:
      trader.print_stats()
      trader.print_configuration()


def back_test_crossing_bot_1min():
   file_list = "Data1Min2/historic_data_list.txt"

   master_file_list = hf.create_master_file_list(file_list)
   # for item in master_file_list: Sanity check
   #    print(item)
   trading_costs = TradingCosts(0.02, 0.005, 0.0000229, 0.00013, 1.00)

   # This takes a long time
   # stop_loss_list = [1.0, 2.5, 3.5, 4.0]
   # moving_average_list = [50, 60, 80, 120]
   # crossing_count_list = [80, 120, 140, 160]
   # crossing_signal_list = [0.25, 0.3, 0.35, 0.45]
   # rsi_period_list = [14, 28, 40]
   # rsi_threshold_list = [10, 15, 25]
   # rsi_buy_list = [40, 50, 60]

   stop_loss_list = [2.5, 3.0]
   moving_average_list = [40, 60, 80]
   crossing_count_list = [60, 80, 100]
   crossing_signal_list = [0.4, 0.5, 0.6]
   rsi_period_list = [14, 22]
   rsi_threshold_list = [10, 15, 20]
   rsi_buy_list = [20, 40]

   start_time = time.time()

   trader_list = []
   for stop_loss in stop_loss_list:
      for moving_avg in moving_average_list:
         for crossing_count in crossing_count_list:
            for crossing_signal in crossing_signal_list:
               for rsi_period in rsi_period_list:
                  for rsi_threshold in rsi_threshold_list:
                     for rsi_buy in rsi_buy_list:
                        trader_list.append(MomentumCrossingBot(stop_loss, moving_avg, crossing_count, crossing_signal, rsi_period, rsi_threshold, rsi_buy, trading_costs, 10000, 200))

   print("Testing Momentum Crossing with %s bots over %s days" % (len(trader_list), len(master_file_list)))
   results = multithreaded_runner(trader_list, master_file_list, 800, 8)

   print("Completed in %s" % (time.time() - start_time))
   results.sort(key=lambda x: x.profit, reverse=True)
   for trader in results[:6]:
      trader.print_stats()
      trader.print_configuration()



def back_test_micro_trader():
   file_list = "Data/historic_data_list.txt"

   master_file_list = hf.create_master_file_list(file_list)
   # for item in master_file_list: Sanity check
   #    print(item)
   trading_costs = TradingCosts(0.02, 0.005, 0.0000229, 0.00013, 1.00)

   # This takes about 2.5 hours
   # moving_average_list = [30, 50, 70, 80, 90, 100]
   # stop_loss_list = [0.5, 1.0, 2.0]
   # momentum_window_list = [5, 10, 15, 20, 30]
   # momentum_threshold_list = [0.05, 0.1, 0.15, 0.2]
   # crossing_count_list = [20, 50, 60, 100, 110, 120]
   # crossing_signal_list = [0.4, 0.5, 0.6]
   # crossing_margin_list = [0.01, 0.04, 0.05, 0.07, 0.1, 0.15, 0.2]

   moving_average_list = [100]
   stop_loss_list = [1.0, 1.5]
   momentum_window_list = [10, 20, 30]
   momentum_threshold_list = [0.05, 0.1, 0.15]
   crossing_count_list = [100, 120]
   crossing_signal_list = [0.4, 0.5]
   crossing_margin_list = [0.15]

   start_time = time.time()

   trader_list = []
   for moving_average in moving_average_list:
      #momentum_window = moving_average
      for stop_loss in stop_loss_list:
         for momentum_window in momentum_window_list:
            for momentum_threshold in momentum_threshold_list:
               for crossing_count in crossing_count_list:
                  for crossing_signal in crossing_signal_list:
                     for crossing_margin in crossing_margin_list:
                        trader_list.append(MicroTraderBot(240, moving_average, stop_loss, momentum_window, momentum_threshold, crossing_count, crossing_signal, crossing_margin, trading_costs, 10000))

   print("Testing Microtrader with %s bots over %s days" % (len(trader_list), len(master_file_list)))
   results = multithreaded_runner(trader_list, master_file_list, 800, 8)

   print("Completed in %s" % (time.time() - start_time))
   results.sort(key=lambda x: x.profit, reverse=True)
   for trader in results[:6]:
      trader.print_stats()
      trader.print_configuration()

if __name__ == "__main__":
   #back_test_micro_trader()
   #back_test_volume_bot()
   #back_test_crossing_bot()
   back_test_crossing_bot_1min()
   #snowball_backtest()
   


