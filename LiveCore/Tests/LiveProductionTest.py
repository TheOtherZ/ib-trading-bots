import logging
import time

from LiveCore.CapitalManager import CapitalManager
from LiveCore.LiveIBInterface import IBInterface
from LiveCore.LiveTraderBase import LiveTraderBase
from TraderCore.TradingCosts import TradingCosts, ibkr_trading_costs

class TestTrader(LiveTraderBase):
   def __init__(self, ticker, name: str = "LiveTestTrader", capital: float = 10000, simulation: bool = False, trading_costs: TradingCosts = ibkr_trading_costs) -> None:
      super().__init__(name, capital, simulation, trading_costs)
      self.ticker = ticker
      self.data_length = 10
      self.capital = capital
      self.state_list = ["open_long", "close_long", "open_short", "close_short", "done"]
      self.current_state = "open_long"
      
      
   def process(self, bar, new_bar=True):
      #print(f"{self.ticker}: {self.current_state}")
      if self.trading_enabled:
         if self.current_state == "open_long":
            self.order(bar.close, 100)
            self.current_state = "close_long"
         elif self.current_state == "close_long" and self.num_held == 100:
            self.order(bar.close, -100)
            self.current_state = "open_short"
         elif self.current_state == "open_short"and self.num_held == 0:
            self.order(bar.close, -100)
            self.current_state = "close_short"
         elif self.current_state == "close_short" and self.num_held == -100:
            self.order(bar.close, 100)
            self.current_state = "done"
      
      #print(f"{self.name}: state: {self.current_state}, num held: {self.num_held}, num pending: {self.num_pending}")
      return super().process()
    

if __name__ == "__main__":
   logging.basicConfig(filename="LiveTest.txt", filemode='a', encoding='utf-8', level=logging.INFO)
   CapitalManager.initialize(65000)
   ip = "127.0.0.1"

   bot_pool = [TestTrader("AMD", name="AMDTest"), TestTrader("INTC", name="INTCTest")]
   ip = "127.0.0.1"
   port = 7498
   connection = 27

   interface = IBInterface(bot_pool)
   interface.enable_after_market()
   # print("Waiting for market to open")
   # while not interface.market_open_in_secs(10 * 60 * 60):
   #    time.sleep(5)
   # print("Market open in 10 minutes or already open")

   interface.start_bots(ip, port, connection, '10 mins', 1)
   
   done = False
   count = 0
   while(not done):
      for bot in bot_pool:
         if bot.current_state != "done":
            done = False
         else:
            done = True
      time.sleep(5)
      print(f"Waiting for done: {count}")
      count += 1
      if count > 10:
         print("Production test did not complete")
         break

   print("Production test complete")
   interface.disconnect()