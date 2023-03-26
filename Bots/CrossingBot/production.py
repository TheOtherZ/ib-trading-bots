import logging
import math
import time

from CrossingBot import CrossingBot
from ibapi.contract import Contract
from TraderCore.CapitalManager import CapitalManager
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
   CapitalManager.initialize(4100)
   ip = "127.0.0.1"
   connection = 1
   # WBD ##########
   connectionWBD = ConnectionInfo(ip, 7497, connection)
   wbdBot = CrossingBot(40, 60, 0.3, 2.0, 8, 25, 24, 0.3, False, capital=10000.0 log_file_name="CrossingProduction.txt", name="ProdWBDBot", log_level=logging.INFO, simulation=False)
   wbdAPI = startBot(connectionWBD, wbdBot, "WBD")

   # META ##########
   connection += 1
   connectionMETA = ConnectionInfo(ip, 7497, connection)
   metaBot = CrossingBot(60, 80, 0.3, 3.0, 8, 15, 12, -0.1, False, capital=10000.0, log_file_name="CrossingProduction.txt", name="ProdMETABot", log_level=logging.INFO, simulation=False)
   metaAPI= startBot(connectionMETA, metaBot, "META")

   # CCL ##########
   connection += 1
   connectionCCL = ConnectionInfo(ip, 7497, 3)
   cclBot = CrossingBot(40, 100, 0.3, 2.5, 8, 10, 8, 0.3, False, capital=10000.0, log_file_name="CrossingProduction.txt", name="ProdCCLBot", log_level=logging.INFO, simulation=False)
   cclAPI = startBot(connectionCCL, cclBot, "CCL")

   # EPAM ##########
   connection += 1
   connectionEPAM = ConnectionInfo(ip, 7497, connection)
   epamBot = CrossingBot(9, 5, 0.2, 1.0, 4, 10, 12, -1, True, capital=10000.0, log_file_name="CrossingProduction.txt", name="ProdEPAMBot", log_level=logging.INFO, simulation=False)
   epamAPI = startBot(connectionEPAM, epamBot, "EPAM")

   # MRNA ##########
   connection += 1
   connectionMRNA = ConnectionInfo(ip, 7497, connection)
   mrnaBot = CrossingBot(12, 10, 0.2, 2.0, 4, 15, 8, -0.1, False, capital=10000.0, log_file_name="CrossingProduction.txt", name="ProdMRNABot", log_level=logging.INFO, simulation=False)
   mrnaAPI = startBot(connectionMRNA, mrnaBot, "MRNA")

   # F ##########
   connection += 1
   connectionF = ConnectionInfo(ip, 7497, connection)
   fBot = CrossingBot(9, 5, 0.1, 2.5, 12, 10, 12, -1, True, capital=10000.0, log_file_name="CrossingProduction.txt", name="ProdFBot", log_level=logging.INFO, simulation=False)
   fAPI = startBot(connectionF, fBot, "F")

   api_list = [wbdAPI, metaAPI, cclAPI, epamAPI, mrnaAPI, fAPI]

   # Handle multi-day?
   while True:
      in_val = input("Enter q to quit or symbol to manually close:\n")
      if str(in_val) == 'q':
         print("Manual disconnect")
         for api in api_list:
            api.disconnect()
         break
      
      for api in api_list:
         if api.contract.symbol == str(in_val):
            api.closePosition()

if __name__ == "__main__":
   multiProduction()
