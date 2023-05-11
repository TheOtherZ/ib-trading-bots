from ibapi.client import EClient
from ibapi.wrapper import EWrapper, BarData
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.utils import decimalMaxString, floatMaxString

import pandas_market_calendars as mcal
import pandas as pd

from LiveCore.LiveTraderBase import LiveTraderBase
from TraderCore.CapitalManager import CapitalManager

import math
import time
from threading import Thread
import logging
logger = logging.getLogger(__name__)

class IBInterface(EClient, EWrapper):
   next_order_id = None
   bot_dict = {} # req_id:{"history_bars": [], "bot": bot, "bar_size": bar_size_seconds, "contract": constract, "last_complete_bar_time": time}

   # Order configuration
   orderType = "MKT"

   # Contract configuration
   secType = "STK"
   exchange = "SMART"
   primaryExchange = "NYSE"
   currency = "USD"

   # Bookeeping
   market_open = False

   def __init__(self, bot_list: list[LiveTraderBase]):
      self.run_thread = Thread(target=self.run, daemon=True)
      self.bot_list = bot_list
      self.pending_orders = {} # ticker: owner_bot_id
      self.after_market_enabled = False

      # Market calendar
      self.nyse_cal = mcal.get_calendar('NYSE')
      self.schedule = self.nyse_cal.schedule(start_date='2023-01-01', end_date='2023-12-31')

      EClient.__init__(self, self)

   def nextValidId(self, orderId: int):
      super().nextValidId(orderId)
      self.next_order_id = orderId

   def blockForConnection(self, wait_time_sec: int):
      secs = 0
      while not isinstance(self.next_order_id, int):
         time.sleep(1)
         secs += 1
         if secs >= wait_time_sec:
            logger.info("Connection failed")
            return False
      return True
   
   def connect(self, host, port, clientId):
      return super().connect(host, port, clientId)
   
   #### Data
   def reqHistoricalData(self, reqId, bot: LiveTraderBase, endDateTime: str, durationStr: str, barSizeSetting: str, whatToShow: str, useRTH: int, formatDate: int, keepUpToDate: bool, chartOptions):
      self.bot_dict[reqId] = {}
      self.bot_dict[reqId]["history_bars"] = []
      self.bot_dict[reqId]["bar_size"] = bar_sizes_secs[barSizeSetting]
      self.bot_dict[reqId]["bot"] = bot
      contract = Contract()
      contract.symbol = bot.ticker
      contract.secType = "STK"
      contract.exchange = "SMART"
      contract.primaryExchange = "NYSE"
      contract.currency = "USD"
      self.bot_dict[reqId]["contract"] = contract
      return super().reqHistoricalData(reqId, contract, endDateTime, durationStr, barSizeSetting, whatToShow, useRTH, formatDate, keepUpToDate, chartOptions)

   def historicalData(self, reqId, bar: BarData):
      self.bot_dict[reqId]["history_bars"].append(bar)

   def historicalDataEnd(self, reqId, start, end):
      super().historicalDataEnd(reqId, start, end)
      # check if market is currently open
      ticker = self.bot_dict[reqId]["bot"].ticker      
      if self.marketOpen():
         self.market_open = True
         print(f"History complete for {ticker}, market open")
         for bar in self.bot_dict[reqId]["history_bars"][:-1]:
            self.bot_dict[reqId]["bot"].process(bar, True)
         self.bot_dict[reqId]["last_bar"] = self.bot_dict[reqId]["history_bars"][-2]
      else:
         print(f"History complete for {ticker}, market closed")
         for bar in self.bot_dict[reqId]["history_bars"]:
            self.bot_dict[reqId]["bot"].process(bar, True)
         self.bot_dict[reqId]["last_bar"] = self.bot_dict[reqId]["history_bars"][-1]

   #### Live data processing
   def historicalDataUpdate(self, reqId: int, bar: BarData):
      if not self.marketOpen() and not self.after_market_enabled:
         print("Bar recieved, but market closed")
         return
      ticker = self.bot_dict[reqId]["bot"].ticker
      new_bar = True if self.bot_dict[reqId]["last_bar"].date != bar.date else False
      self.bot_dict[reqId]["bot"].trading_enabled = True
      num_pending = self.bot_dict[reqId]["bot"].process(bar, new_bar)
      if num_pending != 0 and ticker not in self.pending_orders:
         #TODO: make order
         # Open
         if self.bot_dict[reqId]["bot"].num_held == 0 and CapitalManager.get_available_capitol() > self.bot_dict[reqId]["bot"].capital:
            CapitalManager.take_capitol(self.bot_dict[reqId]["bot"].capital)
         # Close
         elif self.bot_dict[reqId]["bot"].num_held != 0:
            CapitalManager.add_capitol(self.bot_dict[reqId]["bot"].capital)
         
         order = Order()
         order.orderType = self.orderType
         order.transmit = True
         order.totalQuantity = num_pending
         self.pending_orders[ticker] = [self.next_order_id, reqId] # way to link this order back to the bot
         self.placeOrder(self.next_order_id, self.bot_dict[reqId]["contract"], order)
         self.reqIds(-1)
      
      self.bot_dict[reqId]["last_bar"] = bar

   def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
      logger.info(f'{self.contract.symbol}: orderStatus - orderid: {orderId} status: {status} num filled: {filled} remaining: {remaining} AverageFill: {avgFullPrice}')
      if status == "Filled" and remaining == 0:
         for key in self.pending_orders:
            if self.pending_orders[key][0] == orderId:
               print(f"Confirmed order of: {filled} {key} @ {avgFullPrice}")
               self.bot_dict[self.pending_orders[key][1]]["bot"].confirm_order(float(avgFullPrice), float(filled))
               del(self.pending_orders[key])


   def closePosition(self, ticker):
      """ Used to manually close position"""
      for key in self.bot_dict:
         if self.bot_dict[key]["bot"].ticker == ticker:
            order = Order()
            order.orderType = self.orderType
            order.transmit = True
            order.totalQuantity = -self.bot_dict[key]["bot"].num_held
            self.placeOrder(self.next_order_id,self.bot_dict[key]["contract"], order)
            self.reqIds(-1)
            info_str = f"Manually closing {self.contract.symbol}!"
            print(self.esclame_string(info_str))
            logger.info(info_str)
            CapitalManager.add_capitol(self.bot_dict[key]["bot"].capital)
            break

   #### Positions
   def position(self, account: str, contract: Contract, position, avgCost: float):
            super().position(account, contract, position, avgCost)
            if int(position) != 0:
               for bot in self.bot_list:
                  if bot.ticker == contract.symbol:
                     print(f"Existing position found: {decimalMaxString(position)}, Symbol: {contract.symbol}, Avg cost: {floatMaxString(avgCost)}")
                     bot.num_held = float(position)
                     bot.average_price = float(avgCost)
   
   def reqPositions(self):
      """IMPORTANT: only request at startup"""
      self.position_started = True
      super().reqPositions()
             
   def positionEnd(self):
      self.position_started = False
      super().positionEnd()
      print("PositionEnd")
      self.cancelPositions()

   def start_bots(self, host, port, clientId, bar_size: str):
      self.connect(host, port, clientId)   
      self.run_thread.start()
      if not self.blockForConnection(5):
         print("Connection failed!")
         return
      
      # Get existing positions
      self.reqPositions()
      while (self.position_started):
         time.sleep(1)
      
      for bot in self.bot_list:
         history_seconds = bot.data_length * bar_sizes_secs[bar_size] * 60
         if history_seconds >= 86400:
            history_days = math.ceil(bot.data_length / 39.0)
            history_str = f'{history_days} D'
         else:
            history_str = f'{history_seconds} S'
         self.reqHistoricalData(self.next_order_id, bot, '',  history_str, bar_size, "TRADES", 0, 1, True, [])
         self.next_order_id += 1

   #### Helper functions
   @staticmethod
   def esclame_string(msg) -> str:
      return "**************************\n" + msg + "\n**************************"
   
   def marketOpen(self):
      today = pd.Timestamp.today('UTC')
      if self.nyse_cal.open_at_time(self.schedule, today):
         return True
      else:
         return False
   
   
bar_sizes_secs = {
   "1 secs": 1,
   "5 secs": 5,
   "10 secs": 10,
   "15 secs": 15,
   "30 secs": 30,
   "1 min": 60,
   "2 mins": 60 * 2,
   "3 mins": 60 * 3,
   "5 mins": 60 * 5,
   "10 mins": 60 * 10,
   "15 mins": 60 * 15,
   "20 mins": 60 * 20,
   "30 mins": 60 * 30,
   "1 hour": 60 * 60 * 1,
   "2 hours": 60 * 60 * 2,
   "3 hours": 60 * 60 * 3,
   "4 hours": 60 * 60 * 4,
   "8 hours": 60 * 60 * 8,
   "1 day": 60 * 60 * 24,
   "1 week": 60 * 60 * 24 * 7,
   "1 month": 60 * 60 * 24 * 7 * 4 #TODO:???
}

if __name__ =="__main__":
   #Testing
   from Bots.MeanRegression.MeanRegressionBotLive import MeanRegressionBotLive
   bot_pool = [
      # MeanRegressionBotLive(120, 80, 10, 2.0, 8, 5.0, "WBD", 10000, simulation=False),
      # MeanRegressionBotLive(120, 80, 10, 2.0, 8, 5.0, "NVDA", 10000, simulation=False),
      # MeanRegressionBotLive(120, 80, 10, 2.0, 8, 5.0, "ETSY", 10000, simulation=False),
      # MeanRegressionBotLive(120, 80, 16, 2.0, 8, 3.0, "PYPL", 10000, simulation=False),
      # MeanRegressionBotLive(80, 60, 10, 2.0, 8, 4.0, "TSLA", 10000, simulation=False),
      MeanRegressionBotLive(80, 60, 10, 2.0, 8, 3.0, "META", 10000, simulation=False),
      # MeanRegressionBotLive(120, 80, 10, 2.0, 8, 5.0, "CZR", 10000, simulation=False),
      # MeanRegressionBotLive(120, 80, 10, 2.0, 8, 4.0, "STLD", 10000, simulation=False),
      # MeanRegressionBotLive(120, 80, 10, 2.0, 8, 3.0, "NXPI", 10000, simulation=False),
      # MeanRegressionBotLive(120, 80, 10, 2.0, 8, 4.0, "SPGI", 10000, simulation=False),
      # MeanRegressionBotLive(120, 80, 10, 2.0, 8, 5.0, "CHRW", 10000, simulation=False),
      # MeanRegressionBotLive(60, 80, 10, 2.0, 8, 3.0, "UAL", 10000, simulation=False),
      # MeanRegressionBotLive(120, 80, 10, 2.0, 8, 3.0, "PWR", 10000, simulation=False),
      # MeanRegressionBotLive(120, 80, 10, 2.0, 8, 4.0, "DVA", 10000, simulation=False),
      # MeanRegressionBotLive(80, 60, 10, 2.0, 8, 3.0, "BBWI", 10000, simulation=False)
   ]
   ip = "127.0.0.1"
   port = 7498
   connection = 27

   interface = IBInterface(bot_pool)
   interface.after_market_enabled = True
   interface.start_bots(ip, port, connection, '3 mins')

   while True:
      in_val = input("Enter q to quit or symbol to manually close:\n")
      if str(in_val) == 'q':
         print("Manual disconnect")
         interface.disconnect()
         break
      else:
         interface.closePosition(str(in_val))