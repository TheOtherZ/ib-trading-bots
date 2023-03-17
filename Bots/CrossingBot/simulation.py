from Simulation.Simulator import simulate_single_source, simulate_ticker_group, simulate_single_bar_file, simulate_single_trader
from CrossingBot import CrossingBot
def build_trader_list(frame="short"):
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
   elif frame == "fast":
      average_window_list = [9, 12]
      crossing_window_list = [5, 8]
      crossing_threshold_list = [.2, .3]
      stop_loss_list = [1.0, 2.0]
      rsi_list = [4, 8]
      purge_list = [10, 15]
      sell_rsi_list = [8]
      sell_crossing_list = [-0.1, 0.1, 0.4, 0.7]
   elif frame == "mixed":
      average_window_list = [9, 12, 20, 40, 60, 80]
      crossing_window_list = [5, 8, 10]
      crossing_threshold_list = [.2, .3]
      stop_loss_list = [1.0, 1.5, 2.0, 2.5]
      rsi_list = [4, 8, 12]
      purge_list = [5, 10, 15]
      sell_rsi_list = [8, 12]
      sell_crossing_list = [-0.1, 0.1, 0.2]
   elif frame == "long":
      average_window_list = [40, 60, 80]
      crossing_window_list = [40, 60, 80, 100]
      crossing_threshold_list = [0.2, .3]
      stop_loss_list = [2.0, 2.5, 3.0]
      rsi_list = [8, 12, 30]
      purge_list = [10, 15, 25]
      sell_rsi_list = [8, 12, 24]
      sell_crossing_list = [-0.1, 0.1, 0.3]

   for average_window in average_window_list:
      for crossing_window in crossing_window_list:
         for crossing_threshold in crossing_threshold_list:
            for stop_loss in stop_loss_list:
               for rsi in rsi_list:
                  for purge in purge_list:
                     for sell_rsi in sell_rsi_list:
                        for sell_crossing in sell_crossing_list:
                            if rsi <= average_window + crossing_window and sell_rsi <= average_window + crossing_window:
                                bot = CrossingBot(average_window, crossing_window, crossing_threshold, stop_loss, rsi, purge, sell_rsi, sell_crossing)
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


def simSP500():
   test_trader_list = build_trader_list("short")

   ticker_dir = "C:\\Users\\ezimb\\source\\repos\\IBBotTransfer\\IBBot\\Data\\SP500_10Min\\"
   ticker_file = "S&P500-Symbols.csv"
   #ticker_file = "short_list.csv"

   simulate_ticker_group(test_trader_list, ticker_dir, ticker_file, top_traders=5, sav_file="short-sp500.txt")

   test_trader_list = build_trader_list("long")
   simulate_ticker_group(test_trader_list, ticker_dir, ticker_file, top_traders=5, sav_file="long-sp500.txt")

if __name__ == "__main__":
   simSP500()
   #simSingle()