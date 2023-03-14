from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.wrapper import EWrapper
from ibapi.wrapper import BarData

import datetime
import time
from threading import Thread

import pandas_market_calendars as mcal

class Historycollector(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)
        self.log_file = None
        self.run_thread = Thread(target=self.run, daemon=True)
        self.collection_complete = False

    def start_loop(self):
        self.run_thread.start()


    def historicalData(self, reqId, bar: BarData):
        self.recordBarDatabar(bar)
        #print("HistoricalData. ReqId:", reqId, "BarData.", bar)

    def historicalDataEnd(self, reqId, start, end):
        super().historicalDataEnd(reqId, start, end)
        self.log_file.close()
        self.collection_complete = True
        #print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)

    def recordBarDatabar(self, bar: BarData):
        self.log_file.write("%s,%s,%s,%s,%s,%s,%s,%s\n" % (bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume, bar.average, bar.barCount))

    def open_log_file(self, file_name):
        self.log_file = open(file_name, 'w')
        self.collection_complete = False
        self.log_file.write("Date,Open,High,Low,Close,Volume,Average,BarCount\n")

    def close_log_file(self):
        if self.log_file is not None:
            self.log_file.close()
            self.log_file = None

if __name__ =="__main":
   # Get 1 day
   # Contracts
   underlying_contract = Contract()
   underlying_contract.symbol = "QQQ"
   underlying_contract.secType = "STK"
   underlying_contract.exchange = "SMART"
   underlying_contract.currency = "USD"

   short_contract = Contract()
   short_contract.symbol = "SQQQ"
   short_contract.secType = "STK"
   short_contract.exchange = "SMART"
   short_contract.currency = "USD"

   long_contract = Contract()
   long_contract.symbol = "TQQQ"
   long_contract.secType = "STK"
   long_contract.exchange = "SMART"
   long_contract.currency = "USD"

   collector = Historycollector()
   collector.connect("192.168.50.243", 7497, 1)
   collector.start_loop()
   time.sleep(2)

   data_dir = "Data2/"
   file_name_file = open(data_dir + "historic_data_list_TEMP.txt", "a")
   today = datetime.datetime.now()
   now = today.replace(hour=22, minute=0, second=0)
    
    # Data collection QQQ
   log_name = data_dir + underlying_contract.symbol + "_" + now.strftime("%b-%d-%Y-%H-%M") + ".csv"
   collector.open_log_file(log_name)
   collector.reqHistoricalData(4102, underlying_contract, now.strftime("%Y%m%d-%H:%M:%S"), str(int(60 * 60 * 6.5)) + " S", "30 secs", "TRADES", 1, 1, False, [])
   # Wait for data to come down
   while not collector.collection_complete:
      time.sleep(0.5)

   file_name_file.write(log_name + "\n")

   collector.close_log_file()
   
   # Data collection SQQ
   log_name = data_dir + short_contract.symbol + "_" + now.strftime("%b-%d-%Y-%H-%M") + ".csv"
   collector.open_log_file(log_name)
   collector.reqHistoricalData(4103, short_contract, now.strftime("%Y%m%d-%H:%M:%S"), str(int(60 * 60 * 6.5)) + " S", "30 secs", "TRADES", 1, 1, False, [])
   # Wait for data to come down
   while not collector.collection_complete:
      time.sleep(0.5)

   file_name_file.write(log_name + "\n")

   collector.close_log_file()

   # Data collection TQQ
   log_name = data_dir + long_contract.symbol + "_" + now.strftime("%b-%d-%Y-%H-%M") + ".csv"
   collector.open_log_file(log_name)
   collector.reqHistoricalData(4104, long_contract, now.strftime("%Y%m%d-%H:%M:%S"), str(int(60 * 60 * 6.5)) + " S", "30 secs", "TRADES", 1, 1, False, [])

   # Wait for data to come down
   while not collector.collection_complete:
      time.sleep(0.5)

   file_name_file.write(log_name + "\n")

   collector.close_log_file()

   #Cleanup
   file_name_file.close()
   collector.disconnect()


if __name__ =="__main__":
   # Contracts
   underlying_contract = Contract()
   underlying_contract.symbol = "QQQ"
   underlying_contract.secType = "STK"
   underlying_contract.exchange = "SMART"
   underlying_contract.currency = "USD"

   short_contract = Contract()
   short_contract.symbol = "SQQQ"
   short_contract.secType = "STK"
   short_contract.exchange = "SMART"
   short_contract.currency = "USD"

   long_contract = Contract()
   long_contract.symbol = "TQQQ"
   long_contract.secType = "STK"
   long_contract.exchange = "SMART"
   long_contract.currency = "USD"

   collector = Historycollector()
   collector.connect("192.168.50.243", 7497, 1)
   collector.start_loop()
   time.sleep(2)
   
   data_dir = "Data1Min2/tempData/"
   file_name_file = open(data_dir + "historic_data_list2.txt", "a")
   end_of_days = []
   nyse = mcal.get_calendar('NYSE')
   days = nyse.valid_days(start_date='2022-09-06', end_date='2022-10-09')
   for day in days:
      new_day = day.to_pydatetime().replace(hour=22)
      end_of_days.append(new_day)

   print(len(end_of_days))

   for end_day in reversed(end_of_days):
      print(end_day.strftime("%b-%d-%Y-%H-%M"))
      # Data collection QQQ
      log_name = data_dir + underlying_contract.symbol + "_" + end_day.strftime("%b-%d-%Y-%H-%M") + ".csv"
      collector.open_log_file(log_name)
      collector.reqHistoricalData(4102, underlying_contract, end_day.strftime("%Y%m%d-%H:%M:%S"), str(int(60 * 60 * 6.5)) + " S", "1 min", "TRADES", 1, 1, False, [])
      # Wait for data to come down
      while not collector.collection_complete:
         time.sleep(0.5)

      file_name_file.write(log_name + "\n")

      collector.close_log_file()
      
      # Data collection SQQ
      log_name = data_dir + short_contract.symbol + "_" + end_day.strftime("%b-%d-%Y-%H-%M") + ".csv"
      collector.open_log_file(log_name)
      collector.reqHistoricalData(4102, short_contract, end_day.strftime("%Y%m%d-%H:%M:%S"), str(int(60 * 60 * 6.5)) + " S", "1 min", "TRADES", 1, 1, False, [])
      # Wait for data to come down
      while not collector.collection_complete:
         time.sleep(0.5)

      file_name_file.write(log_name + "\n")

      collector.close_log_file()

      # Data collection TQQ
      log_name = data_dir + long_contract.symbol + "_" + end_day.strftime("%b-%d-%Y-%H-%M") + ".csv"
      collector.open_log_file(log_name)
      collector.reqHistoricalData(4102, long_contract, end_day.strftime("%Y%m%d-%H:%M:%S"), str(int(60 * 60 * 6.5)) + " S", "1 min", "TRADES", 1, 1, False, [])

      # Wait for data to come down
      while not collector.collection_complete:
         time.sleep(0.5)

      file_name_file.write(log_name + "\n")

      collector.close_log_file()

   #Cleanup
   file_name_file.close()
   collector.disconnect()

    