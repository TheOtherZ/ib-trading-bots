from LiveCore.LiveIBInterface import IBInterface
from DataCollection.HistoryCollection import HistoryCollector, ConnectionInfo
from ibapi.contract import Contract

import pandas as pd
import os
import time

sp_info_file_name = "S&P500-Info.csv"
#sp_symbols_file_name = "etf-symbols.csv"
sp_symbols_file_name = "S&P500-Symbols.csv"


def getSandP():
   table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
   df = table[0]
   df.to_csv(sp_info_file_name)
   df.to_csv(sp_symbols_file_name, columns=['Symbol'])

if __name__ == "__main__":
   #getSandP()

   contract = Contract()
   contract.secType = "STK"
   contract.exchange = "SMART"
   contract.primaryExchange = "NYSE"
   contract.currency = "USD"

   connection = ConnectionInfo("127.0.0.1", 7498, 31)

   with open(sp_symbols_file_name) as sp_symbol_file:
      for line in sp_symbol_file:
         idx, ticker = line.strip("\n").split(",")
         path = "Tickers/" + ticker
         if not os.path.exists(path):
            os.makedirs(path)

         print("Collecting data for " + ticker)
         collector = HistoryCollector(contract, connection)
         collector.contract.symbol = ticker
         collector.setLogDir(path + "/")
         start_time = time.time()
         #collector.collectDayData('2020-09-06', '2023-09-02', "5 mins")
         status = collector.collectDayData('2023-09-25', '2023-09-26', "30 mins")
         if status:
            with open("failed_tickers.txt", "w") as f:
               f.write(ticker + "\n")
         print(f"Completed in {time.time() - start_time}S")

   collector.disconnect()

