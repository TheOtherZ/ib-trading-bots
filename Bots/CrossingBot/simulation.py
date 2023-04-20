from Simulation.Simulator import simulate_single_source, simulate_ticker_group, simulate_single_bar_file, simulate_single_trader
from CrossingBot import CrossingBot
def build_trader_list(frame="short", strange=False) -> CrossingBot:
   trader_list = []

   if frame == "short":
      average_window_list = [9, 12, 20]
      crossing_window_list = [5, 8, 10]
      crossing_threshold_list = [.1, .2, .3]
      stop_loss_list = [1.5, 2.0, 2.5]
      rsi_list = [4, 8, 12]
      purge_list = [5, 10, 15]
      sell_rsi_list = [8, 12]
      sell_crossing_list = [-0.1, 0.1, 0.3]
      strange_list = [strange]
   elif frame == "fast":
      average_window_list = [9, 12]
      crossing_window_list = [5, 8]
      crossing_threshold_list = [.2, .3]
      stop_loss_list = [1.0, 2.0]
      rsi_list = [4, 8]
      purge_list = [10, 15]
      sell_rsi_list = [8]
      sell_crossing_list = [-0.1, 0.1, 0.4, 0.7]
      strange_list = [strange]
   elif frame == "mixed":
      average_window_list = [9, 12, 20, 40, 60, 80]
      crossing_window_list = [5, 8, 10]
      crossing_threshold_list = [.2, .3]
      stop_loss_list = [1.0, 1.5, 2.0, 2.5]
      rsi_list = [4, 8, 12]
      purge_list = [5, 10, 15]
      sell_rsi_list = [8, 12]
      sell_crossing_list = [-0.1, 0.1, 0.2]
      strange_list = [strange]
   elif frame == "long":
      average_window_list = [40, 60, 80]
      crossing_window_list = [40, 60, 80, 100]
      crossing_threshold_list = [0.2, .3]
      stop_loss_list = [2.0, 2.5, 3.0]
      rsi_list = [8, 12, 30]
      purge_list = [10, 15, 25]
      sell_rsi_list = [8, 12, 24]
      sell_crossing_list = [-0.1, 0.1, 0.3]
      strange_list = [strange]

   for average_window in average_window_list:
      for crossing_window in crossing_window_list:
         for crossing_threshold in crossing_threshold_list:
            for stop_loss in stop_loss_list:
               for rsi in rsi_list:
                  for purge in purge_list:
                     for sell_rsi in sell_rsi_list:
                        for sell_crossing in sell_crossing_list:
                            for strange in strange_list:
                              if rsi <= average_window + crossing_window and sell_rsi <= average_window + crossing_window:
                                 bot = CrossingBot(average_window, crossing_window, crossing_threshold, stop_loss, rsi, purge, sell_rsi, sell_crossing, strange)
                                 bot.trading_enabled = True
                                 trader_list.append(bot)

   return trader_list


def simSingle():
   print("Simulating Single")
   # trader = CrossingBot(9, 5, 0.2, 1.0, 4, 10, 12, simulation=True)
   # simulate_single_trader(trader, "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SP500_10Min\\Tickers\\EPAM\\EPAM_2023-02-28_10 mins.csv")
   
   # trader = CrossingBot(40, 60, 0.3, 1.0, 8, 15, 12, simulation=True)
   # simulate_single_trader(trader, "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SP500_10Min\\Tickers\\META\\META_2023-02-28_10 mins.csv")
   for crossing in [-1.0, -.4, -.3, -.2, -.1, 0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0]:
      trader = CrossingBot(40, 60, 0.3, 1.0, 8, 15, 12, crossing, simulation=True)
      simulate_single_trader(trader, "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SP500_10Min\\Tickers\\META\\META_2023-02-28_10 mins.csv")

def simMRNA():
   # trader = CrossingBot(12, 10, 0.2, 2.0, 4, 15, 8, -0.1,strange_mode=False, simulation=True)
   # simulate_single_trader(trader, "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SP500_10Min\\Tickers\\MRNA\\MRNA_2023-02-28_10 mins.csv")
   # trader = CrossingBot(12, 10, 0.2, 2.0, 4, 15, 8, -0.1,strange_mode=True, simulation=True)
   # simulate_single_trader(trader, "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SP500_10Min\\Tickers\\MRNA\\MRNA_2023-02-28_10 mins.csv")
   #('MRNA', 55506.56721357904, -6.151908992, 349, 1975.2427864209997, '12, 10, 0.2, 2.0, 4, 15, 8, -0.1')
   test_trader_list = build_trader_list("short")
   test_trader_list += build_trader_list("long")

   for trader in test_trader_list:
      simulate_single_trader(trader, "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SP500_10Min\\Tickers\\MRNA\\MRNA_2023-02-28_10 mins.csv", False)
   
   test_trader_list.sort(reverse=True)
   with open("MRNA-Only.txt", 'w') as f:
      for trader in test_trader_list:
         f.write(trader.get_stats() + " " + str(trader) + "\n")

def simMETA():
   test_trader_list = build_trader_list("short")
   test_trader_list += build_trader_list("long")

   for trader in test_trader_list:
      simulate_single_trader(trader, "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SP500_10Min\\Tickers\\META\\META_2023-02-28_10 mins.csv", False)
   
   test_trader_list.sort(reverse=True)
   with open("META-Only.txt", 'w') as f:
      for trader in test_trader_list:
         f.write(trader.get_stats() + " " + str(trader) + "\n")

def simEPAM():
   trader = CrossingBot(9, 5, 0.2, 1.0, 4, 10, 12, -1, True, simulation=True)
   simulate_single_trader(trader, "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SP500_10Min\\Tickers\\EPAM\\EPAM_2023-02-28_10 mins.csv")
   
   # test_trader_list = build_trader_list("short", True)
   # test_trader_list += build_trader_list("long", True)

   # for trader in test_trader_list:
   #    trader.strange_mode = True
   #    simulate_single_trader(trader, "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SP500_10Min\\Tickers\\EPAM\\EPAM_2023-02-28_10 mins.csv", False)
   
   # test_trader_list.sort(reverse=True)
   # with open("EPAM-Only.txt", 'w') as f:
   #    for trader in test_trader_list:
   #       f.write(trader.get_stats() + " " + str(trader) + "\n")


def simSP500():
   test_trader_list = build_trader_list("short")

   ticker_dir = "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SP500_10Min\\"
   #ticker_file = "S&P500-Symbols.csv"
   ticker_file = "short_list.csv"

   #simulate_ticker_group(test_trader_list, ticker_dir, ticker_file, top_traders=5, sav_file="short-sp500.txt")

   test_trader_list = build_trader_list("long")
   simulate_ticker_group(test_trader_list, ticker_dir, ticker_file, top_traders=5, sav_file="long-sp500.txt", print_len=None)

def simBest():
   test_trader_list = []
   test_trader_list.append(CrossingBot(40, 60, 0.3, 2.0, 8, 25, 24, 0.3, False)) # WBD
   test_trader_list.append(CrossingBot(40, 100, 0.3, 2.5, 8, 10, 8, 0.3, False)) # CCL
   test_trader_list.append(CrossingBot(60, 80, 0.3, 3.0, 8, 15, 12, -0.1, False)) # META
   test_trader_list.append(CrossingBot(80, 60, 0.2, 2.0, 8, 15, 8, 0.3, False)) # SBNY
   test_trader_list.append(CrossingBot(12, 10, 0.2, 2.0, 4, 15, 8, -0.1, False)) # MRNA
   test_trader_list.append(CrossingBot(9, 5, 0.2, 1.0, 4, 10, 12, -1, True)) # EPAM
   test_trader_list.append(CrossingBot(9, 8, 0.1, 1.5, 8, 10, 8, -1, True)) # F
   test_trader_list.append(CrossingBot(9, 5, 0.2, 2.0, 4, 15, 4, True)) # AMD
   test_trader_list.append(CrossingBot(80, 100, 0.2, 2.5, 8, 25, 8, 0.1, False)) # DISH
   for trader in test_trader_list:
      trader.trading_enabled = True
   ticker_dir = "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SP500_10Min\\"
   ticker_file = "S&P500-Symbols.csv"
   simulate_ticker_group(test_trader_list, ticker_dir, ticker_file, top_traders=3, sav_file="BEST-sp500.txt", print_len=None)

if __name__ == "__main__":
   simSP500()
   #simSingle()
   #simMETA()
   #simEPAM()
   #simBest()