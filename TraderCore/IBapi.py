from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.utils import decimalMaxString, floatMaxString
from ibapi.wrapper import BarData
from ibapi.wrapper import EWrapper
from TraderCore.TraderBase import TraderBase

from threading import Thread
import logging
import time

class ConnectionInfo(object):
   def __init__(self, ip: str, port: int, id: int) -> None:
     self.ip = ip
     self.port = port
     self.id = id
   
   def get_info(self) -> list:
      return self.ip, self.port, self.id
   
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


class IBapi(EWrapper, EClient):
   next_order_id = None
   bar_size_secs = 0

   last_tick_time = 0
   last_complete_bar = None
   first_bar_of_day = True
   last_tick = None

   def __init__(self, bot: TraderBase, symbol: str):
      self.run_thread = Thread(target=self.run, daemon=True)
      self.historic_bars = []
      self.bot = bot
      self.bot.trading_enabled = False
      self.symbol = symbol

      self.contract = Contract()
      self.contract.symbol = symbol
      self.contract.secType = "STK"
      self.contract.exchange = "SMART"
      self.contract.currency = "USD"

      self.order = Order()
      self.order.orderType = "MKT"
      self.order.tif = "GTC"
      self.order.outsideRth =True
      self.order.transmit = True
      EClient.__init__(self, self)

   def start_loop(self):
      self.run_thread.start()

   def historicalData(self, reqId, bar: BarData):
      #print(str(reqId) + " " + str(bar))
      self.historic_bars.append(bar)

   def historicalDataEnd(self, reqId, start, end):
      super().historicalDataEnd(reqId, start, end)
      #Remove last bar because it is incomplete: TODO
      #self.last_tick = self.historic_bars.pop()
      for bar in self.historic_bars:
         #print(str(reqId) + " " + str(bar))
         self.bot.process(bar)
      self.bot.trading_enabled = True
      print("End History")
   
   def historicalDataUpdate(self, reqId, bar: BarData):
      #print(str(reqId) + " " + str(bar))
      tick_time = time.time()
      bar_update = True

      if self.last_tick.date != bar.date and self.last_complete_bar_time is None:
         print(f"First Bar")
         self.last_complete_bar_time = self.last_tick_time
      elif self.last_complete_bar_time is not None and self.last_tick.date != bar.date and tick_time - self.last_complete_bar_time + 1 > self.bar_size_secs:
         print(f"Bar miss: {tick_time - self.last_complete_bar_time}")
         self.last_complete_bar_time = self.last_tick_time
      elif self.last_complete_bar_time is not None and tick_time - self.last_complete_bar_time + 1 > self.bar_size_secs:
         print(f"Bar close: {tick_time - self.last_complete_bar_time}")
         self.last_complete_bar_time = tick_time
      else:
         bar_update = False

      if bar_update:
         print(str(reqId) + " " + str(bar))
         open_or_close, order_type, num_pending = self.bot.process(bar)
         if (open_or_close == "open" and order_type == "long") or (open_or_close == "close" and order_type == "short"):
            self.order.action = "BUY"
            self.order.totalQuantity = num_pending
            print(f"BUY: {open_or_close}, {order_type}")
            self.placeOrder(self.next_order_id, self.contract, self.order)
            self.reqIds(-1)
            #TODO:
            if open_or_close == "open":
               self.bot.confirm_open(bar.close, num_pending)
            else:
               self.bot.confirm_close(bar.close, num_pending)
         elif (open_or_close == "open" and order_type == "short") or (open_or_close == "close" and order_type == "long"):
            self.order.action = "SELL"
            self.order.totalQuantity = num_pending
            print(f"SELL: {open_or_close}, {order_type}")
            self.placeOrder(self.next_order_id, self.contract, self.order)
            self.reqIds(-1)
            #TODO:
            if open_or_close == "open":
               self.bot.confirm_open(bar.close, num_pending)
            else:
               self.bot.confirm_close(bar.close, num_pending)

      self.last_tick_time = tick_time
      self.last_tick = bar

   def blockForConnection(self, wait_time_sec: int):
      secs = 0
      while not isinstance(self.next_order_id, int):
         time.sleep(1)
         secs += 1
         if secs >= wait_time_sec:
            logging.info("Connection failed")
            return False
      return True

   def reqHistoricalData(self, reqId, contract: Contract, endDateTime: str, durationStr: str, barSizeSetting: str, whatToShow: str, useRTH: int, formatDate: int, keepUpToDate: bool, chartOptions):
      self.bar_size_secs = bar_sizes_secs[barSizeSetting]
      return super().reqHistoricalData(reqId, contract, endDateTime, durationStr, barSizeSetting, whatToShow, useRTH, formatDate, keepUpToDate, chartOptions)

   # Orders
   def nextValidId(self, orderId: int):
      super().nextValidId(orderId)
      self.next_order_id = orderId
      logging.info(f'The next valid order id is: {self.next_order_id}')
   
   def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
      logging.info(f'orderStatus - orderid: {orderId} status: {status} filled: {filled} remaining: {remaining} lastFillPrice: {lastFillPrice}')

   def openOrder(self, orderId, contract, order, orderState):
      logging.info(f'openOrder id: {orderId} {contract.symbol} {contract.secType} @ \
                   {contract.exchange}: {order.action} {order.orderType} {order.totalQuantity} {orderState.status}')

   def execDetails(self, reqId, contract, execution):
      logging.info(f'Order Executed: {reqId} {contract.symbol} {contract.secType} {contract.currency} {execution.execId} {execution.orderId} {execution.shares} {execution.lastLiquidity}')

   def position(self, account: str, contract: Contract, position, avgCost: float):
             super().position(account, contract, position, avgCost)
             print("Position.", "Account:", account, "Symbol:", contract.symbol, "SecType:",
                   contract.secType, "Currency:", contract.currency,
                   "Position:", decimalMaxString(position), "Avg cost:", floatMaxString(avgCost))
             
   def positionEnd(self):
      super().positionEnd()
      print("PositionEnd")
      self.cancelPositions()
      
def test_connection():
   intc_contract = Contract()
   intc_contract.symbol = "INTC"
   intc_contract.secType = "STK"
   intc_contract.exchange = "SMART"
   intc_contract.currency = "USD"

   qqq_contract = Contract()
   qqq_contract.symbol = "QQQ"
   qqq_contract.secType = "STK"
   qqq_contract.exchange = "SMART"
   qqq_contract.currency = "USD"

   base_trader = TraderBase(simulation=False, log_level=logging.INFO, log_file_name="connectionTesting.txt")
   test_api = IBapi(base_trader, "INTC")

   connection = ConnectionInfo("192.168.50.243", 7497, 1)

   test_api.connect(*connection.get_info())   
   test_api.start_loop()
   if not test_api.blockForConnection(5):
      return
   
   test_api.reqOpenOrders()

   test_api.order.action = "SELL"
   test_api.order.totalQuantity = 100
   test_api.order.outsideRth = True
   test_api.placeOrder(test_api.next_order_id, test_api.contract, test_api.order)

   time.sleep(5)

   test_api.reqPositions()
   test_api.reqIds(-1)

   time.sleep(5)

   test_api.order.action = "BUY"
   test_api.order.totalQuantity = 100
   test_api.placeOrder(test_api.next_order_id, test_api.contract, test_api.order)

   time.sleep(5)

   test_api.reqPositions()

   time.sleep(5)

   test_api.disconnect()
   
   #test_api.reqHistoricalData(test_api.next_order_id, test_api.contract, '',  f'{60} S', '30 secs', "TRADES", 0, 1, True, [])


if __name__ == "__main__":
   while True:
      test_connection()
      time.sleep(60*2)
