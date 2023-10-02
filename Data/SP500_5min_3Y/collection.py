from LiveCore.LiveIBInterface import IBInterface
from DataCollection.FlatHistoryCollection import FlatHistoryCollector, ConnectionInfo
from ibapi.contract import Contract

import datetime
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

def closeToReboot():
    """Return true if x is in the range [start, end]"""
    now = datetime.datetime.now()
    start = datetime.datetime.now().replace(hour=19, minute=55)
    #start.replace(hour=19, minute=50)
    end = datetime.datetime.now().replace(hour=20, minute=5)
    #end.replace(hour=20, minute=10)
    #TODO
   #  print(now.strftime("%H:%M"))
   #  print(start.strftime("%H:%M"))
   #  print(end.strftime("%H:%M"))
    if now > start and now < end:
        return True
    else:
        return False
    
def main():
   #getSandP()

   contract = Contract()
   contract.secType = "STK"
   contract.exchange = "SMART"
   contract.primaryExchange = "NYSE"
   contract.currency = "USD"

   connection = ConnectionInfo("127.0.0.1", 7497, 31)
   collector = FlatHistoryCollector(contract, connection)
   collector.startup()
   started = True

   with open(sp_symbols_file_name) as sp_symbol_file:
      for line in sp_symbol_file:
         idx, ticker = line.strip("\n").split(",")
         path = "Tickers/" + ticker
         if not os.path.exists(path):
            os.makedirs(path)
         
         if not IBInterface.marketOpen() and not IBInterface.market_open_in_secs(60*10) and not closeToReboot():
            if not started:
               print("Restarting after blackout period")
               connection.id = connection.id + 1
               collector = FlatHistoryCollector(contract, connection)
               collector.startup()
               started = True
            print("Collecting data for " + ticker)
            collector.contract.symbol = ticker
            start_time = time.time()
            status = collector.collectDayData('3 Y', '20230902-12:00:00', "5 mins", path +"/")
            if status:
               with open("failed_tickers.txt", "w") as f:
                  f.write(ticker + "\n")
            print(f"Completed in {time.time() - start_time}S")
         else:
            if started:
               print("Shutting down for blackout period")
               collector.disconnect()
               started = False
               while IBInterface.marketOpen() or IBInterface.market_open_in_secs(60*10) or closeToReboot():
                  time.sleep(30)

   collector.disconnect()



if __name__ == "__main__":
   main()
