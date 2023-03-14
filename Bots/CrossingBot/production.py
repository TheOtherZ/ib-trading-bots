import logging
from CrossingBot import CrossingBot
import TraderCore.IBInterface as ibapi

from ib_insync import *

import time
import math
   
def altProduction():
   bot = CrossingBot(24, 10, 0.1, 2.0, 8, log_file_name="CrossingProduction.txt", name="ProdCrossingBot", log_level=logging.INFO)
   bot.simulation = False

   ib = IB()
   ib.connect("192.168.50.243", 7497, 14)

   # Get historic data
   contract = Stock('INTC', 'SMART', 'USD')
   # 10 minute bars
   history_seconds = bot.data_length * 10 * 60


   def onBarUpdate(bars, hasNewBar):
      print(bars[-1].close)
      onBarUpdate.bar_count += 1
      if hasNewBar:
         print(f'Bar Count: {onBarUpdate.bar_count}')
         onBarUpdate.bar_count = 0
   onBarUpdate.bar_count = 0

   bars = ib.reqHistoricalData(
        contract,
        endDateTime='',
        durationStr=f'{history_seconds} S',
        barSizeSetting='1 min',
        whatToShow='TRADES',
        useRTH=True,
        formatDate=1,
        keepUpToDate=True)
   
   bars.updateEvent += onBarUpdate
   
   for bar in bars:
      bar.wap = bar.average
      print(bar)

   print("History End")

   ib.sleep(60 * 5)
   ib.cancelHistoricalData(bars)
   ib.disconnect()

def production():
   bot = CrossingBot(24, 10, 0.1, 2.0, 8, log_file_name="CrossingProduction.txt", name="ProdCrossingBot", log_level=logging.INFO, simulation=False)
   #TODO
   # bot.num_held = 527
   # bot.holding = "short"
   # bot.average_price = 28.44
   # #Wait till market open:
   # print("Waiting")
   # time.sleep(60 * 37)
   # print("Starting")

   ib_api = ibapi.IBapi(bot, "INTC")

   connection = ibapi.ConnectionInfo("192.168.50.243", 7497, 1)

   ib_api.connect(*connection.get_info())   
   ib_api.start_loop()
   if not ib_api.blockForConnection(5):
      return
   
   # 10 minute bars
   history_seconds = bot.data_length * 10 * 60
   
   ib_api.reqHistoricalData(ib_api.next_order_id, ib_api.contract, '',  f'{history_seconds} S', '10 mins', "TRADES", 1, 1, True, [])

def startBot(connection_info, bot, api):
   contract = Contract()
   contract.symbol = api.contract.symbol
   contract.secType = "STK"
   contract.exchange = "SMART"
   contract.primaryExchange = "NYSE"
   contract.currency = "USD"
   api.contract = contract

   bot.trading_enabled = False

   api.connect(*connection_info.get_info())   
   api.start_loop()
   if not api.blockForConnection(5):
      return
   time.sleep(3)

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


def multiProduction():
   #ip = "192.168.50.243"
   ip = "127.0.0.1"
   # WBD ##########
   connectionWBD = ibapi.ConnectionInfo(ip, 7497, 1)
   wbdBot = CrossingBot(60, 100, 0.3, 2.0, 36, 25, 24, log_file_name="CrossingProduction.txt", name="ProdWBDBot", log_level=logging.INFO, simulation=False)
   wbdAPI = ibapi.IBInterface(wbdBot, Contract(symbol="WBD"))
   startBot(connectionWBD, wbdBot, wbdAPI)
   time.sleep(10)

   # META ##########
   connectionMETA = ibapi.ConnectionInfo(ip, 7497, 2)
   metaBot = CrossingBot(40, 60, 0.3, 2.0, 8, 15, 12, log_file_name="CrossingProduction.txt", name="ProdMETABot", log_level=logging.INFO, simulation=False)
   metaAPI = ibapi.IBInterface(metaBot, Contract(symbol="META"))
   startBot(connectionMETA, metaBot, metaAPI)

   # AMD ##########
   # connectionAMD = ibapi.ConnectionInfo(ip, 7497, 3)
   # amdBot = CrossingBot(80, 40, 0.3, 2.5, 8, 25, 12, log_file_name="CrossingProduction.txt", name="ProdAMDBot", log_level=logging.INFO, simulation=False)
   # amdAPI = ibapi.IBInterface(amdBot, Contract(symbol="AMD"))
   # startBot(connectionAMD, amdBot, amdAPI)

   # EPAM ##########
   connectionEPAM = ibapi.ConnectionInfo(ip, 7497, 3)
   epamBot = CrossingBot(9, 5, 0.2, 1.0, 4, 10, 12, log_file_name="CrossingProduction.txt", name="ProdEPAMBot", log_level=logging.INFO, simulation=False)
   epamAPI = ibapi.IBInterface(epamBot, Contract(symbol="EPAM"))
   startBot(connectionEPAM, epamBot, epamAPI)

   # MRNA ##########
   connectionMRNA = ibapi.ConnectionInfo(ip, 7497, 4)
   mrnaBot = CrossingBot(9, 8, 0.1, 1.0, 4, 10, 8, log_file_name="CrossingProduction.txt", name="ProdMRNABot", log_level=logging.INFO, simulation=False)
   mrnaAPI = ibapi.IBInterface(mrnaBot, Contract(symbol="MRNA"))
   startBot(connectionMRNA, mrnaBot, mrnaAPI)

   # Script usually started pre-market
   print("Waiting for market open")
   while not mrnaAPI.marketOpen():
      time.sleep(5)
   print("Market open")

   # Handle multi-day?
   while True:
      in_val = input()
      time.sleep(10)
      if str(in_val) == 'q':
         print("Manual disconnect")
         wbdAPI.disconnect()
         epamAPI.disconnect()
         metaAPI.disconnect()
         mrnaAPI.disconnect()
         break
      elif not mrnaAPI.marketOpen():
         print("Market closed")
         time.sleep(30) # give time for stuff to close out
         wbdAPI.disconnect()
         epamAPI.disconnect()
         metaAPI.disconnect()
         mrnaAPI.disconnect()
         break

if __name__ == "__main__":
   multiProduction()
