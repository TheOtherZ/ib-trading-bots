from Simulation.FileProcessing import make_flat_bars_from_master
from Bots.CrossingBot.CrossingBot import CrossingBot
import matplotlib.pyplot as plt

if __name__ == "__main__":
   data_1_dir = "/home/zimbra/development/IBBot/Data/INTC_10Min_Bars_Very_Long/"
   data_1_master = "INTC_2020-01-01_2023-02-14_10 mins.txt"
   # data_1_dir = "/home/zimbra/development/IBBot/Data/INTC_10Min_Bars_Long/"
   # data_1_master = "INTC_2020-01-01_2023-01-09_10 mins.txt"
   data_2_dir = "/home/zimbra/development/IBBot/Data/QQQ_10Min_Bars_Long/"
   data_2_master = "QQQ_2020-01-01_2023-02-14_10 mins.txt"

   data_1_bars = make_flat_bars_from_master(data_1_master, data_1_dir)
   data_2_bars = make_flat_bars_from_master(data_2_master, data_2_dir)

   data_2_price = [x.wap for x in data_1_bars]

   #crossing_bot = CrossingBot(12, 10, 0.1, 2.0, 8, 30000, True) Good past 2 years
   crossing_bot = CrossingBot(12, 10, 0.1, 2.0, 8, 30000, False)
   crossing_profit = []

   time = []
   t = 0
   for bar in data_1_bars:
      crossing_bot.process(bar)
      crossing_profit.append(crossing_bot.profit)
      time.append(t)
      t += 1
   crossing_bot.print_stats()


   fig, ax1 = plt.subplots(constrained_layout=True)
   ax2 = ax1.twinx()

   data_start = 5400
   data_end = 6000
   ax1.plot(time, crossing_profit, 'm')
   ax2.plot(time, data_2_price, 'b')
   plt.show()