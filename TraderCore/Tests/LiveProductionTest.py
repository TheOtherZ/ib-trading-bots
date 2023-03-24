import logging
import time
from ibapi.contract import Contract
from TraderCore.TraderBase import TraderBase
from TraderCore.CapitalManager import CapitalManager
from TraderCore.ConnectionInfo import ConnectionInfo
import TraderCore.IBInterface as ibapi

class TestTrader(TraderBase):
   def __init__(self, capital=5000, simulation: bool = False, log_level: int = logging.info, log_file_name: str = "", name: str = "none_bot", leverage: float = 1, save_dir="Save/") -> None:
      super().__init__(simulation=simulation, log_level=log_level, log_file_name=log_file_name, name=name, leverage=leverage, save_dir=save_dir)
      self.data_length = 10
      self.capital = capital
      self.state_list = ["open_long", "close_long", "open_short", "close_short", "done"]
      self.current_state = "open_long"

   def process(self, bar):
      if self.trading_enabled:
         if self.current_state == "open_long":
            self.open_position(bar.close, 100, "long")
            self.current_state = "close_long"
         elif self.current_state == "close_long":
            self.close_position(bar.close, 100)
            self.current_state = "open_short"
         elif self.current_state == "open_short":
            self.open_position(bar.close, 100, "short")
            self.current_state = "close_short"
         elif self.current_state == "close_short":
            self.close_position(bar.close, 100)
            self.current_state = "done"
         
      return super().process(bar)
    

def startBot(connection_info, bot, symbol):
   contract = Contract()
   contract.symbol = symbol
   contract.secType = "STK"
   contract.exchange = "SMART"
   contract.primaryExchange = "NYSE"
   contract.currency = "USD"
   api = ibapi.IBInterface(bot, contract)

   bot.trading_enabled = False

   api.connect(*connection_info.get_info())   
   api.start_loop()
   if not api.blockForConnection(5):
      return

   api.reqPositions()
   while (api.position_started):
      time.sleep(1)

   # 30 second bars
   history_seconds = bot.data_length * 30

   api.reqHistoricalData(api.next_order_id, api.contract, '',  f'{history_seconds} S', '30 secs', "TRADES", 0, 1, True, [])

   while (api.history_started):
      time.sleep(1)

   return api

if __name__ == "__main__":
   CapitalManager.initialize(65000)
   ip = "127.0.0.1"
   connection = 0
    # INTC ##########
   connection += 1
   connectionINTC = ConnectionInfo(ip, 7497, connection)
   metaBot = TestTrader(5000, log_file_name="TestProduction.txt", name="ProdTestBot", log_level=logging.INFO, simulation=False)
   testAPI= startBot(connectionINTC, metaBot, "INTC")

   while(testAPI.bot.current_state != "done"):
       time.sleep()

   print("Production test complete")
   testAPI.disconnect()