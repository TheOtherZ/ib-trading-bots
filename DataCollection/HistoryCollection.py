from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.wrapper import EWrapper
from ibapi.wrapper import BarData
from TraderCore.ConnectionInfo import ConnectionInfo

import datetime
import time
from threading import Thread

import pandas_market_calendars as mcal

class HistoryCollector(EClient, EWrapper):
   def __init__(self, contract: Contract, connection_info: ConnectionInfo, root_dir=None):
      EClient.__init__(self, self)
      self.log_file = None
      self.run_thread = Thread(target=self.run, daemon=True)
      self.collection_complete = False
      self.contract = contract
      self.connection_info = connection_info
      self.root_dir = root_dir

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

   def open_log_file(self, file_name):
      self.log_file = open(file_name, 'w')
      self.collection_complete = False
      self.log_file.write("Date,Open,High,Low,Close,Volume,Average,BarCount\n")

   def close_log_file(self):
      if self.log_file is not None:
         self.log_file.close()
         self.log_file = None

   def collectDayData(self, start_date: str, end_date: str, interval: str) -> None:
      self.connect(*self.connection_info.get_info())
      self.start_loop()
      time.sleep(2)

      # Create list of end of trading day days
      end_of_days = []
      nyse = mcal.get_calendar('NYSE')
      days = nyse.valid_days(start_date=start_date, end_date=end_date)
      for day in days:
         new_day = day.to_pydatetime().replace(hour=22)
         end_of_days.append(new_day)

      # List of day data file names
      master_file_name = self.contract.symbol + "_" + start_date + "_" + end_date + "_" + interval + ".txt"
      if self.root_dir is not None:
            master_file_name = self.root_dir + master_file_name
      master_file_handle = open(master_file_name, 'a')

      trading_day_seconds = str(int(60 * 60 * 6.5)) + " S"

      for trading_day in end_of_days:
         log_name = trading_day.strftime("%Y-%m-%d_") + self.contract.symbol + ".csv"
         if self.root_dir is not None:
            log_name = self.root_dir + log_name
         master_file_handle.write(log_name + "\n")
         self.open_log_file(log_name)
         self.reqHistoricalData(4102, self.contract, trading_day.strftime("%Y%m%d-%H:%M:%S"),  trading_day_seconds, interval, "TRADES", 1, 1, False, [])
         
         # Wait for data to download to finish
         while not self.collection_complete:
            time.sleep(0.5)

         self.close_log_file()
      
      # Cleanup
      master_file_handle.close()
      self.disconnect()
