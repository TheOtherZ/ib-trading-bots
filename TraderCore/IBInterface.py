from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.wrapper import EWrapper
from ibapi.wrapper import BarData
from ibapi.utils import decimalMaxString, floatMaxString

from TraderCore.TraderBase import TraderBase
from TraderCore.CapitalManager import CapitalManager

import pandas_market_calendars as mcal
import pandas as pd

from threading import Thread
import logging
import time

class IBInterface(EClient, EWrapper):
   def __init__(self, bot: TraderBase, contract: Contract):
      EClient.__init__(self, self)
      self.run_thread = Thread(target=self.run, daemon=True)
      self.next_order_id = None
      self.order = Order()
      self.order.orderType = "MKT"
      self.order.transmit = True
      self.order.tif = "GTC"
      self.order.outsideRth =True

      self.bot = bot
      self.contract = contract

      self.historic_bars = []
      self.last_bar = None
      self.market_open = False
      self.bar_size_secs = 0

      self.last_complete_bar_time = 0
      self.last_bar_time = 0
      self.bar_complete = False
      self.missed_bars = -1
      self.after_market_enabled = False

      # Market calendar
      self.nyse_cal = mcal.get_calendar('NYSE')
      self.schedule = self.nyse_cal.schedule(start_date='2023-01-01', end_date='2023-12-31')

      # Long run logic
      self.already_started = False
      self.position_started = False
      self.history_started = False

   ##################################### Data source

   def marketOpen(self):
      today = pd.Timestamp.today('UTC')
      if self.nyse_cal.open_at_time(self.schedule, today):
         return True
      else:
         return False

   def reqHistoricalData(self, reqId, contract: Contract, endDateTime: str, durationStr: str, barSizeSetting: str, whatToShow: str, useRTH: int, formatDate: int, keepUpToDate: bool, chartOptions):
      self.bar_size_secs = bar_sizes_secs[barSizeSetting]
      self.history_started = True
      return super().reqHistoricalData(reqId, contract, endDateTime, durationStr, barSizeSetting, whatToShow, useRTH, formatDate, keepUpToDate, chartOptions)

   def historicalData(self, reqId, bar: BarData):
      self.historic_bars.append(bar)

   def historicalDataEnd(self, reqId, start, end):
      self.history_started = False
      super().historicalDataEnd(reqId, start, end)

      if self.already_started:
         print(f"{self.contract.symbol}: Already started, not updating history")
         self.last_complete_bar_time = time.time() + self.bar_size_secs + 100
         return
      else:
         self.already_started = True

      # check if market is currently open
      if self.marketOpen():
         print("History complete, market open")
         self.market_open = True
      else:
         print(f"{self.contract.symbol}: History complete, market closed")
      
      if self.market_open:
         self.last_complete_bar_time = time.time() + self.bar_size_secs + 100
         for bar in self.historic_bars[:-1]:
            self.bot.process(bar)
      else:
         for bar in self.historic_bars:
            self.bot.process(bar)
      self.last_bar = self.historic_bars[-1]

   def historicalDataUpdate(self, reqId: int, bar: BarData):
      if not self.marketOpen() and not self.after_market_enabled:
         print("Bar recieved, but market closed")
         return
      bar_time = time.time()
      bar_to_process = bar
      process_now = False

      if self.bar_complete:
         self.missed_bars += 1

      if not self.market_open:
         # trader was started outside market hours and we are receiving the first bars
         self.market_open = True
         self.last_complete_bar_time = bar_time + self.bar_size_secs + 2
      elif self.last_bar.date != bar.date:
         if self.bar_complete:
            # First bar after succeeding in catching last bar from a set
            if self.missed_bars > 0:
               print(f"{self.contract.symbol}: New bar started, bars missed: {self.missed_bars}")
            self.bar_complete = False
         else:
            print(f"{self.contract.symbol}: First bar or bar miss")
            bar_to_process = self.last_bar
            self.bar_complete = True
            process_now = True
            if not self.bot.trading_enabled:
               logging.info(f"{self.contract.symbol}: trading enabled")
               self.bot.trading_enabled = True
         self.missed_bars = -1
         self.last_complete_bar_time = self.last_bar_time
      elif bar_time - self.last_complete_bar_time + 1 > self.bar_size_secs:
         self.bar_complete = True
         process_now = True
         self.last_complete_bar_time = bar_time
         self.missed_bars = -1

      if process_now:
         self.processBar(bar_to_process)

      self.last_bar = bar
      self.last_bar_time = bar_time

   #################### Processing

   def processBar(self, bar: BarData):
      open_or_close, order_type, num_pending = self.bot.process(bar)
      if open_or_close == "open" and order_type == "long":
         self.order.action = "BUY"
         if CapitalManager.get_available_capitol() >= self.bot.capital:
            CapitalManager.take_capitol(self.bot.capital)
            self.order.totalQuantity = num_pending
            info_str = f"{open_or_close}, {order_type} with bar: {str(bar)}"
            print(self.esclame_string(info_str))
            logging.info(info_str)
            self.placeOrder(self.next_order_id, self.contract, self.order)
            self.reqIds(-1)
         else:
            info_str = f"Atempted {open_or_close}, {order_type} with symbol: {self.contract.symbol}, but no more money"
            print(self.esclame_string(info_str))
            logging.info(info_str)
      elif open_or_close == "close" and order_type == "short":
         self.order.action = "BUY"
         self.order.totalQuantity = num_pending
         CapitalManager.add_capitol(self.bot.capital)
         info_str = f"{open_or_close}, {order_type} with bar: {str(bar)}"
         print(self.esclame_string(info_str))
         logging.info(info_str)
         self.placeOrder(self.next_order_id, self.contract, self.order)
         self.reqIds(-1)
      elif open_or_close == "open" and order_type == "short":
         self.order.action = "SELL"
         if CapitalManager.get_available_capitol() >= self.bot.capital:
            CapitalManager.take_capitol(self.bot.capital)
            self.order.totalQuantity = num_pending
            info_str = f"{open_or_close}, {order_type} with bar: {str(bar)}"
            print(self.esclame_string(info_str))
            logging.info(info_str)
            self.placeOrder(self.next_order_id, self.contract, self.order)
            self.reqIds(-1)
         else:
            info_str = f"Atempted {open_or_close}, {order_type} with symbol: {self.contract.symbol}, but no more money"
            print(self.esclame_string(info_str))
            logging.info(info_str)
      elif open_or_close == "close" and order_type == "long":
         self.order.action = "SELL"
         self.order.totalQuantity = num_pending
         CapitalManager.add_capitol(self.bot.capital)
         info_str = f"{open_or_close}, {order_type} with bar: {str(bar)}"
         print(self.esclame_string(info_str))
         logging.info(info_str)
         self.placeOrder(self.next_order_id, self.contract, self.order)
         self.reqIds(-1)

   def closePosition(self):
      """ Used to manually close position"""
      if self.bot.holding == "short":
         self.order.action = "BUY"
      elif self.bot.holding == "long":
         self.order.action = "SELL"
      self.order.totalQuantity = self.bot.num_held
      CapitalManager.add_capitol(self.bot.capital)
      info_str = f"Manually closing {self.contract.symbol}!"
      print(self.esclame_string(info_str))
      logging.info(info_str)
      self.bot.open_or_close ="close"
      self.placeOrder(self.next_order_id, self.contract, self.order)
      self.reqIds(-1)


   ###################### Running

   def error(self, reqId, errorCode: int, errorString: str, advancedOrderRejectJson = ""):
      super().error(reqId, errorCode, errorString, advancedOrderRejectJson)
      #print(f"Error: {errorCode}, {errorString}")

   def blockForConnection(self, wait_time_sec: int):
      secs = 0
      while not isinstance(self.next_order_id, int):
         time.sleep(1)
         secs += 1
         if secs >= wait_time_sec:
            logging.info("Connection failed")
            return False
      return True
   
   def start_loop(self):
      self.run_thread.start()
   
   ############################## Orders
   def nextValidId(self, orderId: int):
      super().nextValidId(orderId)
      self.next_order_id = orderId

   def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
      logging.info(f'{self.contract.symbol}: orderStatus - orderid: {orderId} status: {status} num filled: {filled} remaining: {remaining} AverageFill: {avgFullPrice}')
      if status == "Filled" and remaining == 0:
         if self.bot.open_or_close == "open":
            print(f"{self.contract.symbol}: Confirm open")
            self.bot.confirm_open(float(avgFullPrice), float(filled))
         elif self.bot.open_or_close == "close":
            print(f"{self.contract.symbol}: Confirm close")
            self.bot.confirm_close(float(avgFullPrice), float(filled))

   def position(self, account: str, contract: Contract, position, avgCost: float):
             super().position(account, contract, position, avgCost)
             if contract.symbol == self.contract.symbol and int(position) != 0:
               print(f"Existing position found: {decimalMaxString(position)}, Symbol: {contract.symbol}, Avg cost: {floatMaxString(avgCost)}")
               self.bot.confirm_open(float(avgCost), abs(float(position)))
               if position > 0:
                  self.bot.holding = "long"
               else:
                  self.bot.holding = "short"
   
   def reqPositions(self):
      self.position_started = True
      super().reqPositions()
             
   def positionEnd(self):
      self.position_started = False
      super().positionEnd()
      print("PositionEnd")
      self.cancelPositions()

   @staticmethod
   def esclame_string(msg) -> str:
      return "**************************\n" + msg + "\n**************************"

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
