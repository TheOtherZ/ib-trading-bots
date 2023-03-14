from time import time
import matplotlib.pyplot as plt

from MomentumCrossingTrader import MomentumCrossingBot

from Simulator import snowball_backtest, snowball_backtest_1min, adaptive_backtest_1min

import HelperFunctions as hf

master_file_name = "Data1Min2/historic_data_list.txt"

def get_QQQ_day_price_list():
   master_file_list = hf.create_master_file_list(master_file_name)
   open_prices = []
   for group in reversed(master_file_list):
      with open(group[0], 'r') as qqq_file:
         x = 0
         for line in qqq_file.readlines():
            if x == 0:
               pass
            else:
               open_bar = hf.make_bar(*list(line.split(",")))
               open_prices.append(open_bar.open)
               break
            x += 1

   return open_prices

def plot_snowball_profit():
   starting_cap = 20000
   trader = snowball_backtest_1min(master_file_name, starting_cap, 800)
   profit_list = trader.day_profit_list
   day_percent_change = []
   total_profit = []
   time_list = []
   end_day_holding = 0

   for x in range(len(profit_list)):
      if x == 0:
         total_profit.append(profit_list[x])
      else:
         total_profit.append(total_profit[x-1] + profit_list[x])
      day_percent_change.append((profit_list[x] / (total_profit[-1] + starting_cap)) * 100)
      time_list.append(x)

   qqq_prices = get_QQQ_day_price_list()

   fig, ax1 = plt.subplots(constrained_layout=True)
   ax2 = ax1.twinx()
   # cursor = Cursor(ax1)
   # fig.canvas.mpl_connect('motion_notify_event', cursor.on_mouse_move)
   
   ax1.plot(time_list, total_profit, 'm')
   ax2.plot(time_list, qqq_prices, 'g-')

   print("Biggest Gain: %s, Biggest Loss: %s" % (max(day_percent_change), min(day_percent_change)))

   plt.show()

class Cursor:
    """
    A cross hair cursor.
    """
    def __init__(self, ax):
        self.ax = ax
        self.horizontal_line = ax.axhline(color='k', lw=0.8, ls='--')
        self.vertical_line = ax.axvline(color='k', lw=0.8, ls='--')
        # text location in axes coordinates
        self.text = ax.text(0.72, 0.9, '', transform=ax.transAxes)

    def set_cross_hair_visible(self, visible):
        need_redraw = self.horizontal_line.get_visible() != visible
        self.horizontal_line.set_visible(visible)
        self.vertical_line.set_visible(visible)
        self.text.set_visible(visible)
        return need_redraw

    def on_mouse_move(self, event):
        if not event.inaxes:
            need_redraw = self.set_cross_hair_visible(False)
            if need_redraw:
                self.ax.figure.canvas.draw()
        else:
            self.set_cross_hair_visible(True)
            x, y = event.xdata, event.ydata
            # update the line positions
            self.horizontal_line.set_ydata(y)
            self.vertical_line.set_xdata(x)
            self.text.set_text('x=%1.2f, y=%1.2f' % (x, y))
            self.ax.figure.canvas.draw()

if __name__ == "__main__":
   plot_snowball_profit()