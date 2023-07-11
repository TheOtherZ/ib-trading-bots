from ibapi.client import EClient
from ibapi.wrapper import EWrapper, BarData
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.utils import decimalMaxString, floatMaxString

import pandas_market_calendars as mcal
import pandas as pd

from LiveCore.LiveTraderBase import LiveTraderBase
from LiveCore.CapitalManager import CapitalManager

import math
import time
from threading import Thread, Lock
import logging
logger = logging.getLogger(__name__)

class IBInterface(EClient, EWrapper):
   next_order_id = None
   bot_dict = {} # req_id:{"history_bars": [], "bot": bot, "bar_size": bar_size_seconds, "contract": constract, "last_complete_bar_time": time}

   # Order configuration
   orderType = "MKT"
   time_in_force = "GTC"
   outside_hours = False

   # Contract configuration
   secType = "STK"
   exchange = "SMART"
   primaryExchange = "NYSE"
   currency = "USD"

   # Bookeeping
   market_open = False

   # Monitor
   active_monitor = True

   # Market calendar
   nyse_cal = mcal.get_calendar('NYSE')
   schedule = nyse_cal.schedule(start_date='2023-01-01', end_date='2023-12-31')

   def __init__(self, bot_list: list[LiveTraderBase]):
      self.run_thread = Thread(target=self.run, daemon=True)
      self.monitor_thread = Thread(target=self.monitor, daemon=True)
      self.thread_lock = Lock()
      self.bot_list = bot_list
      self.pending_orders = {} # ticker: owner_bot_id
      self.after_market_enabled = False
      self.active_monitor = True

      # Keep track of attempted opens:
      self.attempted_opens = {}

      EClient.__init__(self, self)

   def start_monitor(self):
      print("Monitor Starting")
      self.active_monitor
      self.monitor_thread.start()
   
   def stop_monitor(self):
      self.active_monitor = False
      if self.monitor_thread.is_alive():
         self.monitor_thread.join(timeout=5)

   def monitor(self):
      service_time = time.time()
      service_interval_secs = 5 * 60
      while self.active_monitor:
         if time.time() > service_time + service_interval_secs:
            for key in self.bot_dict:
               with self.bot_dict[key]["bot"].bot_lock:
                  if self.bot_dict[key]["bot"].watchdog_pet != True and self.bot_dict[key]["bot"].purge_count == 0:
                     print(f"WARNING: {self.bot_dict[key]['bot'].name} has stopped responding")
                  else:
                     self.bot_dict[key]["bot"].watchdog_pet = False

                  if not self.bot_dict[key]["bot"].trade_active:
                     print(f"WARNING: Trading not active for {self.bot_dict[key]['bot'].name}")
            print("Monitor check completed")
            service_time = time.time()
         time.sleep(2)
      
      print("Monitor shutdown")
   
   def enable_after_market(self):
      self.after_market_enabled = True
      self.outside_hours = True

   def disable_after_market(self):
      self.after_market_enabled = False
      self.outside_hours = False

   def disconnect(self):
      self.stop_monitor()
      super().disconnect()

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
         #self.disconnect()
         return
      ticker = self.bot_dict[reqId]["bot"].ticker
      new_bar = True if self.bot_dict[reqId]["last_bar"].date != bar.date else False
      self.bot_dict[reqId]["bot"].trading_enabled = True
      self.bot_dict[reqId]["bot"].live = True
      num_pending = self.bot_dict[reqId]["bot"].process(bar, new_bar)
      with self.thread_lock:
         order_condition = True
         if num_pending != 0 and ticker not in self.pending_orders:
            # Open
            if self.bot_dict[reqId]["bot"].num_held == 0 and CapitalManager.get_available_capital() > self.bot_dict[reqId]["bot"].capital:
               CapitalManager.take_capital(self.bot_dict[reqId]["bot"].capital)
               msg = self.esclame_string("OPEN: " + self.bot_dict[reqId]["bot"].order_msg())
               print(msg)
               logger.info(msg)
               if ticker in self.attempted_opens:
                  del(self.attempted_opens[ticker])
            # Close
            elif self.bot_dict[reqId]["bot"].num_held != 0:
               msg = self.esclame_string("CLOSE: " + self.bot_dict[reqId]["bot"].order_msg())
               CapitalManager.add_capital(self.bot_dict[reqId]["bot"].capital)
               print(msg)
               logger.info(msg)
            else:
               # Condition not met
               if ticker in self.attempted_opens:
                  self.attempted_opens[ticker] += 1
               else:
                  self.attempted_opens[ticker] = 0

               if self.attempted_opens[ticker] % 50 == 0:
                  msg = self.esclame_string("ATTEMPTED OPEN: " + self.bot_dict[reqId]["bot"].name + " " + str(self.attempted_opens[ticker] + 1) + " Times")
                  print(msg)
                  logger.info(msg)
               self.bot_dict[reqId]["bot"].cancel_open_position()
               order_condition = False
            
            if order_condition:
               order = Order()
               order.orderType = self.orderType
               order.tif = self.time_in_force
               order.outsideRth = self.outside_hours
               order.transmit = True
               order.totalQuantity = abs(num_pending)
               if num_pending > 0:
                  order.action = "BUY"
               else:
                  order.action = "SELL"
               self.next_order_id += 1
               self.pending_orders[ticker] = [self.next_order_id, reqId] # way to link this order back to the bot
               self.placeOrder(self.next_order_id, self.bot_dict[reqId]["contract"], order)
      
      self.bot_dict[reqId]["last_bar"] = bar

   def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
      #logger.info(f'TODO TICKER: orderStatus - orderid: {orderId} status: {status} num filled: {filled} remaining: {remaining} AverageFill: {avgFullPrice}')
      if status == "Filled" and remaining == 0:
         with self.thread_lock:
            for key in self.pending_orders:
               if self.pending_orders[key][0] == orderId:
                  msg = f"Confirmed order of: {filled} {key} @ {avgFullPrice}"
                  logger.info(msg)
                  print(self.esclame_string(msg))
                  if self.bot_dict[self.pending_orders[key][1]]["bot"].num_held > 0 or self.bot_dict[self.pending_orders[key][1]]["bot"].num_pending < 0:
                     filled = -filled

                  self.bot_dict[self.pending_orders[key][1]]["bot"].confirm_order(float(avgFullPrice), float(filled))
                  del(self.pending_orders[key])
                  break
      super().orderStatus(orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)


   def closePosition(self, ticker):
      """ Used to manually close position"""
      for key in self.bot_dict:
         if self.bot_dict[key]["bot"].ticker == ticker:
            order = Order()
            order.orderType = self.orderType
            order.transmit = True
            order.totalQuantity = -self.bot_dict[key]["bot"].num_held
            with self.thread_lock:
               self.next_order_id += 1
               self.placeOrder(self.next_order_id,self.bot_dict[key]["contract"], order)
            info_str = f"Manually closing {self.contract.symbol}!"
            print(self.esclame_string(info_str))
            logger.info(info_str)
            CapitalManager.add_capital(self.bot_dict[key]["bot"].capital)
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

   def start_bots(self, host, port, clientId, bar_size: str, outsize_hours=1):
      self.connect(host, port, clientId)   
      self.run_thread.start()
      print("Waiting for connection")
      if not self.blockForConnection(10):
         print("Connection failed!")
         return
      
      # Get existing positions
      self.reqPositions()
      while (self.position_started):
         time.sleep(1)
      
      for bot in self.bot_list:
         # TODO: fix history calculation time
         history_seconds = bot.history_length * bar_sizes_secs[bar_size] * 60
         if history_seconds >= 86400:
            history_days = math.ceil(bot.history_length / 39.0)
            history_str = f'{history_days + 2} D'
            print
         else:
            history_str = f'{history_seconds} S'
         with self.thread_lock:
            self.reqHistoricalData(self.next_order_id, bot, '',  history_str, bar_size, "TRADES", outsize_hours, 1, True, [])
            self.next_order_id += 1
      
      self.start_monitor()

   #### Helper functions
   @staticmethod
   def esclame_string(msg) -> str:
      return "\n**************************\n" + msg + "\n**************************"
   
   @classmethod
   def marketOpen(cls):
      today = pd.Timestamp.today('UTC')
      if cls.nyse_cal.open_at_time(cls.schedule, today):
         return True
      else:
         return False
   
   @classmethod
   def market_open_in_secs(cls, secs: int) -> bool:
      today = pd.Timestamp.today('UTC')
      today += pd.Timedelta(secs, unit='seconds')
      if cls.nyse_cal.open_at_time(cls.schedule, today):
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
