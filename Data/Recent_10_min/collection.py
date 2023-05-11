from DataCollection.FlatHistoryCollection import FlatHistoryCollector, ConnectionInfo
from ibapi.contract import Contract
import pandas as pd
import os
import time

sp_info_file_name = "S&P500-Info.csv"
#sp_symbols_file_name = "etf-symbols.csv"
sp_symbols_file_name = "quick-list-mean-conversion-live.csv"


def getSandP():
   table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
   df = table[0]
   df.to_csv(sp_info_file_name)
   df.to_csv(sp_symbols_file_name, columns=['Symbol'])

if __name__ == "__main__":
   contract = Contract()
   contract.secType = "STK"
   contract.exchange = "SMART"
   contract.primaryExchange = "NYSE"
   contract.currency = "USD"

   connection = ConnectionInfo("127.0.0.1", 4002, 1)
   collector = FlatHistoryCollector(contract, connection)
   collector.startup()
   end_date = "20220607-20:00:00"

   with open(sp_symbols_file_name) as sp_symbol_file:
      for line in sp_symbol_file:
         idx, ticker = line.strip("\n").split(",")
         path = "Tickers/" + ticker
         if not os.path.exists(path):
            os.makedirs(path)

         print("Collecting data for " + ticker)
         collector.contract.symbol = ticker
         start_time = time.time()
         collector.collectDayData('1 D', end_date, "10 mins", path +"/")
         print(f"Completed in {time.time() - start_time}S")

   collector.disconnect()

