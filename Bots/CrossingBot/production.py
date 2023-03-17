import logging
import math
import time

from CrossingBot import CrossingBot
from ibapi.contract import Contract
from TraderCore.CapitolManager import CapitolManager
from TraderCore.ConnectionInfo import ConnectionInfo
import TraderCore.IBInterface as ibapi

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

   # 10 minute bars
   history_seconds = bot.data_length * 10 * 60
   if history_seconds >= 86400:
      history_days = math.ceil(bot.data_length / 39.0)
      history_str = f'{history_days} D'
   else:
      history_str = f'{history_seconds} S'

   api.reqHistoricalData(api.next_order_id, api.contract, '',  history_str, '10 mins', "TRADES", 1, 1, True, [])

   while (api.history_started):
      time.sleep(1)

   return api

def multiProduction():
   CapitolManager.initialize(65000)
   ip = "127.0.0.1"
   connection = 1
   # WBD ##########
   connectionWBD = ConnectionInfo(ip, 7497, connection)
   wbdBot = CrossingBot(60, 100, 0.3, 2.0, 36, 25, 24, log_file_name="CrossingProduction.txt", name="ProdWBDBot", log_level=logging.INFO, simulation=False)
   wbdAPI = startBot(connectionWBD, wbdBot, "WBD")

   # META ##########
   connection += 1
   connectionMETA = ConnectionInfo(ip, 7497, connection)
   metaBot = CrossingBot(40, 60, 0.3, 2.0, 8, 15, 12, log_file_name="CrossingProduction.txt", name="ProdMETABot", log_level=logging.INFO, simulation=False)
   metaAPI= startBot(connectionMETA, metaBot, "META")

   # AMD ##########
   # connection += 1
   # connectionAMD = ConnectionInfo(ip, 7497, connection)
   # amdBot = CrossingBot(80, 40, 0.3, 2.5, 8, 25, 12, log_file_name="CrossingProduction.txt", name="ProdAMDBot", log_level=logging.INFO, simulation=False)
   # amdAPI = ibapi.IBInterface(amdBot, Contract(symbol="AMD"))
   # startBot(connectionAMD, amdBot, amdAPI)

   # EPAM ##########
   connection += 1
   connectionEPAM = ConnectionInfo(ip, 7497, connection)
   epamBot = CrossingBot(9, 5, 0.2, 1.0, 4, 10, 12, log_file_name="CrossingProduction.txt", name="ProdEPAMBot", log_level=logging.INFO, simulation=False)
   epamAPI = startBot(connectionEPAM, epamBot, "EPAM")

   # MRNA ##########
   connection += 1
   connectionMRNA = ConnectionInfo(ip, 7497, connection)
   mrnaBot = CrossingBot(9, 8, 0.1, 1.0, 4, 10, 8, log_file_name="CrossingProduction.txt", name="ProdMRNABot", log_level=logging.INFO, simulation=False)
   mrnaAPI = startBot(connectionMRNA, mrnaBot, "MRNA")

   # Handle multi-day?
   while True:
      in_val = input("Enter q to quit:\n")
      if str(in_val) == 'q':
         print("Manual disconnect")
         wbdAPI.disconnect()
         epamAPI.disconnect()
         metaAPI.disconnect()
         mrnaAPI.disconnect()
         break

if __name__ == "__main__":
   multiProduction()
