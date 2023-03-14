from Simulation.FileProcessing import make_flat_bars_from_master

import matplotlib.pyplot as plt
from ibapi.wrapper import BarData

def compute_difference(data_1_bars: BarData, data_2_bars: BarData):
   diffs = []
   time = []
   x = 0
   for (bar1, bar2) in zip(data_1_bars, data_2_bars):
      percent_data1 = (bar1.close - bar1.open) / bar1.open * 100
      percent_data2 = (bar2.close - bar2.open) / bar2.open * 100
      diffs.append(percent_data1 - percent_data2)
      time.append(x)
      x += 1
   
   return diffs, time

if __name__ == "__main__":
   data_1_dir = "/home/zimbra/development/IBBot/Data/AMD_10Min_Bars/"
   data_1_master = "AMD_2022-01-01_2022-10-27_10 mins.txt"
   data_2_dir = "/home/zimbra/development/IBBot/Data/QQQ_10Min_Bars/"
   data_2_master = "QQQ_2022-01-01_2022-10-27_10 mins.txt"

   data_1_bars = make_flat_bars_from_master(data_1_master, data_1_dir)
   data_2_bars = make_flat_bars_from_master(data_2_master, data_2_dir)

   data_1_price = [x.average for x in data_1_bars]

   change_diff, time = compute_difference(data_1_bars, data_2_bars)

   fig, ax1 = plt.subplots(constrained_layout=True)
   ax2 = ax1.twinx()

   data_start = 5400
   data_end = 6000
   ax1.plot(time[data_start:data_end], change_diff[data_start:data_end], 'm')
   ax2.plot(time[data_start:data_end], data_1_price[data_start:data_end], 'b')
   plt.show()

