from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.wrapper import EWrapper
from ibapi.wrapper import BarData
from TraderCore.ConnectionInfo import ConnectionInfo
import time
import datetime
from threading import Thread

class FlatHistoryCollector(EClient, EWrapper):
   def __init__(self, contract: Contract, connection_info: ConnectionInfo):
      EClient.__init__(self, self)
      self.log_file = None
      self.run_thread = Thread(target=self.run, daemon=True)
      self.collection_complete = False
      self.contract = contract
      self.connection_info = connection_info

   def start_loop(self):
      self.run_thread.start()

   def historicalData(self, reqId, bar: BarData):
      self.recordBarDatabar(bar)
      # print("HistoricalData. ReqId:", reqId, "BarData.", bar)

   def historicalDataEnd(self, reqId, start, end):
      super().historicalDataEnd(reqId, start, end)
      self.log_file.close()
      self.collection_complete = True
      # print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)

   def recordBarDatabar(self, bar: BarData):
      self.log_file.write("%s,%s,%s,%s,%s,%s,%s,%s\n" % (
         bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume, bar.wap, bar.barCount))
      
   def error(self, reqId, errorCode: int, errorString: str, advancedOrderRejectJson = ""):
      if errorCode == 4102:
         print(f"Error occurred: {errorCode} " + errorString)
         self.cancelHistoricalData()
      super().error(reqId, errorCode, errorString, advancedOrderRejectJson)

   def open_log_file(self, file_name):
      self.log_file = open(file_name, 'w')
      self.collection_complete = False
      self.log_file.write("Date,Open,High,Low,Close,Volume,Average,BarCount\n")

   def close_log_file(self):
      if self.log_file is not None:
         self.log_file.close()
         self.log_file = None

   def startup(self):
      self.connect(*self.connection_info.get_info())
      self.start_loop()

   def collectDayData(self, duration, end_date: str, interval: str, dir=None) -> None:
      time.sleep(2)
      if end_date == "":
         str_end_date = str(datetime.datetime.today().date())
      else:
         str_end_date = end_date

      bar_file = self.contract.symbol + "_" + str_end_date + "_" + interval + ".csv"
      if dir is not None:
         bar_file = dir + bar_file
      self.open_log_file(bar_file)
      self.reqHistoricalData(4102, self.contract, end_date,  duration, interval, "TRADES", 1, 1, False, [])
         
      # Wait for data to download to finish
      while not self.collection_complete:
         time.sleep(0.25)

      # Cleanup
      self.close_log_file()

if __name__ == "__main__":
   contract = Contract()
   contract.secType = "STK"
   contract.symbol = "MMM"
   contract.exchange = "SMART"
   contract.currency = "USD"

   connection = ConnectionInfo("192.168.50.243", 7497, 1)
   collector = FlatHistoryCollector(contract, connection)

   collector.collectDayData("2 D", "", "10 mins")