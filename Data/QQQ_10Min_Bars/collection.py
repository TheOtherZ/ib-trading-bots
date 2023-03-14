from DataCollection.HistoryCollection import HistoryCollector, ConnectionInfo
from ibapi.contract import Contract

if __name__ == "__main__":
   contract = Contract()
   contract.symbol = "QQQ"
   contract.secType = "STK"
   contract.exchange = "SMART"
   contract.currency = "USD"

   connection = ConnectionInfo("192.168.50.243", 7497, 1)

   collector = HistoryCollector(contract, connection)

   collector.collectDayData('2022-01-01', '2022-10-27', "10 mins")
