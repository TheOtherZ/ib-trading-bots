import logging

from ibapi.wrapper import BarData

from TraderCore.TraderBase import TraderBase
import TraderCore.Indicators as ind
from Simulation.Simulator import simulate_single_source

class TestTrader(TraderBase):
   def __init__(self, log_file_name: str="", name: str="") -> None:
      super().__init__(log_level=logging.DEBUG, log_file_name=log_file_name, name=name)

if __name__ == "__main__":
   data_1_dir = "/home/zimbra/development/IBBot/Data/AMD_10Min_Bars/"
   data_1_master = "AMD_2022-01-01_2022-10-27_10 mins.txt"
   trader = TestTrader("testTrader.log", "TestTraderBot")
   trader2 = TestTrader("testTrader.log", "TestTrader2Bot")

   quantity = 100
   price1 = 24.27

   trader.open_position(price1, quantity, "long")
   price2 = 25.0
   trader.close_position(price2, quantity)

   trader.print_stats()

   trader.open_position(price2, quantity, "short")
   trader.close_position(price1, quantity)

   trader.print_stats()

   simulate_single_source([trader,trader2], data_1_dir, data_1_master, None, 2)
