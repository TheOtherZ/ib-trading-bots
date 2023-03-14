from DataCollection.HistoryCollection import HistoryCollector, ConnectionInfo
from ibapi.contract import Contract

if __name__ == "__main__":
   contract = Contract()
   contract.symbol = "DOW"
   contract.secType = "STK"
   contract.exchange = "SMART"
   contract.currency = "USD"

   connection = ConnectionInfo("192.168.50.243", 7497, 1)

   collector = HistoryCollector(contract, connection)

   collector.collectDayData('2020-01-01', '2023-01-09', "10 mins")
