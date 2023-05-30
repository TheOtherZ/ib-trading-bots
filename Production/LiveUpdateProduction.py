import logging
import datetime
from LiveCore.CapitalManager import CapitalManager
from LiveCore.LiveIBInterface import IBInterface
from Bots.MeanRegression.MeanRegressionBotLive import MeanRegressionBotLive

def production():
   # print("waiting for market open")
   # time.sleep(28800)
   log_name = "LiveUpdateProduction-" + str(datetime.datetime.today().strftime("%Y-%m-%d")) + ".txt"
   logging.basicConfig(filename=log_name, filemode='a', encoding='utf-8', level=logging.INFO)
   CapitalManager.initialize(41000, "live_capital.json")

   bot_pool = [
      MeanRegressionBotLive(80, 60, 8, 3.0, 8, 3.0, "NFLX", 10000, simulation=False, name="NFLXRegressionBot"),# 7583.869824867004, -1.6565480900000003, 0.75, 24, 10, 14, 6
      MeanRegressionBotLive(120, 80, 8, 3.0, 8, 5.0, "CZR", 10000, simulation=False, name="CZRRegressionBot"),# 7324.501810296009, -478.22711486500083, 0.75, 20, 8, 12, 5
      MeanRegressionBotLive(80, 60, 8, 2.0, 8, 3.0, "UAL", 10000, simulation=False, name="UALRegressionBot"),# 7066.8892743999995, -2.082938158, 0.7, 30, 11, 19, 8
      MeanRegressionBotLive(120, 60, 8, 2.0, 8, 3.0, "WBD", 10000, simulation=False, name="WBDRegressionBot"),# 7019.893072194994, -5.227040000000001, 0.6785714285714286, 28, 11, 17, 9
      MeanRegressionBotLive(120, 60, 8, 3.0, 8, 5.0, "DOV", 10000, simulation=False, name="DOVRegressionBot"),# 6281.482501983997, -3.22, 0.8666666666666667, 30, 17, 13, 3
      MeanRegressionBotLive(120, 80, 8, 3.0, 8, 3.0, "PLD", 10000, simulation=False, name="PLDRegressionBot"),# 5926.668215075005, -1.657885679, 0.8461538461538461, 26, 15, 11, 2
      MeanRegressionBotLive(120, 80, 8, 3.0, 8, 4.0, "CBOE", 10000, simulation=False, name="CBOERegressionBot"),# 5908.830365915994, -47.843579635000694, 0.9285714285714286, 28, 16, 12, 1
      MeanRegressionBotLive(120, 80, 8, 2.0, 8, 5.0, "MTD", 10000, simulation=False, name="MTDRegressionBot"),# 5755.6891361440075, -1.665277799, 0.7272727272727273, 33, 23, 10, 9
      MeanRegressionBotLive(120, 60, 8, 3.0, 8, 3.0, "VRTX", 10000, simulation=False, name="VRTXRegressionBot"),# 5738.408292268006, -1.6590618229999998, 0.8518518518518519, 27, 15, 12, 3
      MeanRegressionBotLive(60, 80, 10, 3.0, 8, 5.0, "MOS", 10000, simulation=False, name="MOSRegressionBot"),# 5671.307076626, -11.509540000000001, 0.9230769230769231, 13, 8, 5, 1
      MeanRegressionBotLive(80, 60, 10, 3.0, 8, 5.0, "ENPH", 10000, simulation=False, name="ENPHRegressionBot"),# 5322.491385163985, -1.65676106, 0.6875, 16, 8, 8, 5
      MeanRegressionBotLive(120, 80, 8, 3.0, 8, 5.0, "CMCSA", 10000, simulation=False, name="CMCSARegressionBot"),# 5276.0835329550055, -2.08268351, 0.875, 24, 9, 15, 1
      MeanRegressionBotLive(120, 80, 10, 3.0, 8, 4.0, "MSI", 10000, simulation=False, name="MSIRegressionBot"),# 5275.265075484007, -562.6757599079991, 0.8181818181818182, 22, 9, 13, 2
      MeanRegressionBotLive(60, 60, 8, 3.0, 8, 5.0, "TRGP", 10000, simulation=False, name="TRGPRegressionBot"),# 5213.969537575007, -11.20798, 0.9285714285714286, 14, 9, 5, 1
      MeanRegressionBotLive(60, 80, 8, 2.0, 8, 3.0, "MKTX", 10000, simulation=False, name="MKTXRegressionBot"),# 5166.528070088001, -1.6469245940000001, 0.8333333333333334, 18, 5, 13, 3
      MeanRegressionBotLive(120, 80, 10, 3.0, 8, 4.0, "SPGI", 10000, simulation=False, name="SPGIRegressionBot"),# 5136.206055447, -1.8399999999999999, 0.9, 20, 12, 8, 1
      MeanRegressionBotLive(120, 60, 8, 2.0, 8, 4.0, "OXY", 10000, simulation=False, name="OXYRegressionBot"),# 5092.999622455999, -13.193249999999999, 0.6190476190476191, 21, 12, 9, 8
      MeanRegressionBotLive(120, 80, 8, 2.0, 8, 3.0, "VRSN", 10000, simulation=False, name="VRSNRegressionBot"),# 4993.051549743001, -1.6591364769999999, 0.8333333333333334, 18, 11, 7, 3
      MeanRegressionBotLive(120, 80, 10, 3.0, 8, 5.0, "NVDA", 10000, simulation=False, name="NVDARegressionBot"),# 4977.929759884, -465.6425976050005, 0.7222222222222222, 18, 11, 7, 5
      MeanRegressionBotLive(120, 80, 10, 2.0, 8, 4.0, "EW", 10000, simulation=False, name="EWRegressionBot"),# 4911.959930928994, -4.5600000000000005, 0.68, 25, 14, 11, 6
      MeanRegressionBotLive(80, 80, 8, 2.0, 8, 5.0, "PYPL", 10000, simulation=False, name="PYPLRegressionBot"),# 4899.828832479, -2.1, 0.631578947368421, 19, 10, 9, 7
      MeanRegressionBotLive(120, 80, 10, 2.0, 8, 4.0, "KHC", 10000, simulation=False, name="KHCRegressionBot"),# 4850.70375334301, -9.47401, 0.8235294117647058, 17, 7, 10, 2
      MeanRegressionBotLive(80, 80, 8, 3.0, 8, 3.0, "AJG", 10000, simulation=False, name="AJGRegressionBot"),# 4800.761664610002, -3.4, 1.0, 23, 16, 7, 0
      MeanRegressionBotLive(120, 80, 8, 3.0, 8, 4.0, "ICE", 10000, simulation=False, name="ICERegressionBot"),# 4652.801978754989, -1.658565122, 0.8620689655172413, 29, 17, 12, 3
      MeanRegressionBotLive(120, 80, 10, 3.0, 8, 5.0, "AMP", 10000, simulation=False, name="AMPRegressionBot"),# 4614.495359110006, -455.6994552449987, 0.8823529411764706, 17, 12, 5, 2
      MeanRegressionBotLive(120, 80, 8, 3.0, 8, 3.0, "EL", 10000, simulation=False, name="ELRegressionBot"),# 4528.923437275005, -62.597765489998835, 0.8461538461538461, 26, 14, 12, 3
      MeanRegressionBotLive(120, 80, 8, 2.0, 8, 5.0, "BKR", 10000, simulation=False, name="BKRRegressionBot"),# 4450.957233343999, -3.8218680099999993, 0.5714285714285714, 28, 13, 15, 12
      MeanRegressionBotLive(120, 40, 8, 3.0, 8, 5.0, "DHI", 10000, simulation=False, name="DHIRegressionBot"),# 4440.298674357016, -4.62, 0.75, 20, 8, 12, 4
      MeanRegressionBotLive(120, 60, 10, 2.0, 8, 4.0, "HST", 10000, simulation=False, name="HSTRegressionBot"),# 4430.518721524999, -5.088644128000002, 0.75, 16, 9, 7, 4
      MeanRegressionBotLive(120, 80, 8, 3.0, 8, 5.0, "PEAK", 10000, simulation=False, name="PEAKRegressionBot"),# 4344.414059057004, -11.10746, 0.8636363636363636, 22, 16, 6, 3

   ]
   ip = "127.0.0.1"
   port = 7498
   connection = 27

   interface = IBInterface(bot_pool)
   interface.after_market_enabled = False
   # print("Waiting for market to open")
   # while not interface.market_open_in_secs(10 * 60 * 60):
   #    time.sleep(5)
   # print("Market open in 10 minutes or already open")

   interface.start_bots(ip, port, connection, '10 mins', 1)

   while True:
      in_val = input("Enter q to quit or symbol to manually close:\n")
      if str(in_val) == 'q':
         print("Manual disconnect")
         interface.disconnect()
         break
      else:
         interface.closePosition(str(in_val))

if __name__ == "__main__":
   production()