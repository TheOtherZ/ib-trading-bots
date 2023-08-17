import logging
import datetime
import time
from multiprocessing import Queue, Process
from LiveCore.CapitalManager import CapitalManager
from LiveCore.LiveIBInterface import IBInterface
from Bots.MeanRegression.MeanRegressionBotLive import MeanRegressionBotLive
from Bots.TrendBot.TrendBot import TrendBot

def production(control_queue: Queue, out_queue: Queue):
   bot_pool = [
      MeanRegressionBotLive(120, 80, 10, 4.0, 8, 3.0, "ALGN", 5000, simulation=False, name="ALGNRegressionBot"),# 12938.32200592398, -1.668166176, 0.7758620689655172, 58, 25, 33, 10
      MeanRegressionBotLive(120, 120, 10, 3.0, 8, 5.0, "LW", 5000, simulation=False, name="LWRegressionBot"),# 11871.847368757011, -1.6577755299999999, 0.7402597402597403, 77, 41, 36, 14
      MeanRegressionBotLive(80, 120, 10, 4.0, 8, 3.0, "WELL", 5000, simulation=False, name="WELLRegressionBot"),# 10811.482140373006, -1.7242324960000004, 0.78, 100, 59, 41, 8
      MeanRegressionBotLive(60, 120, 10, 4.0, 8, 5.0, "DXCM", 5000, simulation=False, name="DXCMRegressionBot"),# 10596.400647368991, -783.3847850272485, 0.7102803738317757, 107, 58, 49, 22
      MeanRegressionBotLive(80, 80, 10, 3.0, 8, 2.0, "EXPE", 5000, simulation=False, name="EXPERegressionBot"),# 10583.320283174997, -1650.2707002920022, 0.7142857142857143, 77, 35, 42, 19
      MeanRegressionBotLive(60, 120, 10, 3.0, 8, 2.0, "NCLH", 5000, simulation=False, name="NCLHRegressionBot"),# 10333.263231181983, -483.6373737619998, 0.6724137931034483, 116, 45, 71, 36
      MeanRegressionBotLive(150, 60, 10, 2.0, 8, 3.0, "WBD", 5000, simulation=False, name="WBDRegressionBot"),# 10313.01846699, -5.227040000000001, 0.6896551724137931, 29, 10, 19, 8
      MeanRegressionBotLive(150, 80, 10, 4.0, 8, 3.0, "PFE", 5000, simulation=False, name="PFERegressionBot"),# 10309.594468736983, -10.5546, 0.7916666666666666, 48, 23, 25, 4
      MeanRegressionBotLive(200, 120, 10, 4.0, 8, 5.0, "NVDA", 5000, simulation=False, name="NVDARegressionBot"),# 10286.583232947258, -661.0869945975006, 0.673469387755102, 49, 23, 26, 13
      MeanRegressionBotLive(80, 80, 10, 3.0, 8, 4.0, "MPWR", 5000, simulation=False, name="MPWRRegressionBot"),# 9914.119908540993, -406.295168525, 0.6538461538461539, 78, 50, 28, 25
      MeanRegressionBotLive(200, 120, 16, 4.0, 8, 5.0, "HAL", 5000, simulation=False, name="HALRegressionBot"),# 9673.963154045, -383.8772061010018, 0.7419354838709677, 31, 17, 14, 7
      MeanRegressionBotLive(200, 120, 16, 4.0, 8, 5.0, "DPZ", 5000, simulation=False, name="DPZRegressionBot"),# 9650.722862932009, -1.82, 0.8285714285714286, 35, 20, 15, 4
      MeanRegressionBotLive(60, 120, 10, 3.0, 8, 5.0, "NRG", 5000, simulation=False, name="NRGRegressionBot"),# 9403.49786954501, -480.4942929879986, 0.7572815533980582, 103, 56, 47, 22
      MeanRegressionBotLive(120, 120, 16, 4.0, 8, 2.0, "AOS", 5000, simulation=False, name="AOSRegressionBot"),# 9241.961966162, -5.65425, 0.8936170212765957, 47, 25, 22, 3
      MeanRegressionBotLive(60, 120, 10, 4.0, 8, 2.0, "SO", 5000, simulation=False, name="SORegressionBot"),# 9127.388680469987, -189.34941527499927, 0.7413793103448276, 116, 66, 50, 4
      MeanRegressionBotLive(150, 120, 10, 4.0, 8, 5.0, "DOV", 5000, simulation=False, name="DOVRegressionBot"),# 9067.869686005011, -3.22, 0.8360655737704918, 61, 32, 29, 6
      MeanRegressionBotLive(80, 80, 10, 4.0, 8, 5.0, "ISRG", 5000, simulation=False, name="ISRGRegressionBot"),# 9067.160620523828, -749.1791992534286, 0.7662337662337663, 77, 42, 35, 12
      MeanRegressionBotLive(120, 120, 10, 4.0, 8, 4.0, "AVGO", 5000, simulation=False, name="AVGORegressionBot"),# 8942.974086934017, -1.653407584, 0.7571428571428571, 70, 43, 27, 9
      MeanRegressionBotLive(120, 120, 10, 4.0, 8, 4.0, "CBOE", 5000, simulation=False, name="CBOERegressionBot"),# 8848.677320263994, -1.6568668579999999, 0.7857142857142857, 70, 38, 32, 6
      MeanRegressionBotLive(120, 120, 10, 2.0, 8, 2.0, "GM", 5000, simulation=False, name="GMRegressionBot"),# 8790.482496845016, -298.6630754099976, 0.6575342465753424, 73, 36, 37, 25
      MeanRegressionBotLive(150, 80, 10, 4.0, 8, 5.0, "CZR", 5000, simulation=False, name="CZRRegressionBot"),# 8705.289335704001, -1.6572850119999996, 0.7441860465116279, 43, 19, 24, 11
      MeanRegressionBotLive(150, 120, 10, 4.0, 8, 4.0, "CF", 5000, simulation=False, name="CFRegressionBot"),# 8699.583552950005, -978.1497299959999, 0.7169811320754716, 53, 27, 26, 13
      MeanRegressionBotLive(80, 120, 16, 4.0, 8, 5.0, "STLD", 5000, simulation=False, name="STLDRegressionBot"),# 8678.764580915016, -685.3898139819956, 0.6885245901639344, 61, 36, 25, 13
      MeanRegressionBotLive(60, 120, 10, 4.0, 8, 3.0, "XEL", 5000, simulation=False, name="XELRegressionBot"),# 8651.499853897029, -6.00607, 0.7410714285714286, 112, 59, 53, 5
      MeanRegressionBotLive(60, 120, 10, 4.0, 8, 2.0, "KEY", 5000, simulation=False, name="KEYRegressionBot"),# 8602.019648634994, -18.14386, 0.696078431372549, 102, 50, 52, 12
      MeanRegressionBotLive(200, 120, 16, 4.0, 8, 5.0, "F", 5000, simulation=False, name="FRegressionBot"),# 8436.057788739003, -1511.4470598249968, 0.65, 40, 17, 23, 11
      MeanRegressionBotLive(120, 120, 10, 4.0, 8, 4.0, "VTR", 5000, simulation=False, name="VTRRegressionBot"),# 8387.191370731987, -2.062775856, 0.7567567567567568, 74, 37, 37, 9
      MeanRegressionBotLive(150, 80, 10, 4.0, 8, 5.0, "TROW", 5000, simulation=False, name="TROWRegressionBot"),# 8359.876787565003, -54.81664701800095, 0.7659574468085106, 47, 21, 26, 7
      MeanRegressionBotLive(80, 120, 10, 4.0, 8, 3.0, "SNPS", 5000, simulation=False, name="SNPSRegressionBot"),# 8333.549315225007, -2.3, 0.7142857142857143, 91, 51, 40, 16
      #TODO remove PYPL and ANSS when closed
      MeanRegressionBotLive(120, 120, 16, 4.0, 8, 5.0, "ANSS", 5000, simulation=False, name="ANSSRegressionBot"),# 7442.174653481999, -1.9, 0.7254901960784313, 51, 25, 26, 10 

      TrendBot(1.0, 200, 36, 3.0, 1.0, "EPAM", capital=5000, simulation=False, name="EPAMTrendBot"),# 28891.919180187953, -79.90057475300006, 0.7571606475716065, 803, 436, 367, 194
      TrendBot(3.0, 40, 24, 3.0, 1.0, "RCL", capital=5000, simulation=False, name="RCLTrendBot"),# 23104.601400981042, -1446.6853098429785, 0.7437020810514786, 913, 459, 454, 233
      TrendBot(2.0, 80, 10, 3.0, 1.0, "ETSY", capital=5000, simulation=False, name="ETSYTrendBot"),# 22717.708481326983, -4926.9851986860085, 0.7414548641542507, 1141, 566, 575, 294
      TrendBot(1.0, 60, 16, 3.0, 1.0, "FTNT", capital=5000, simulation=False, name="FTNTTrendBot"),# 18913.405885482156, -1322.791760194201, 0.7539797395079595, 691, 363, 328, 169
      TrendBot(4.0, 60, 16, 3.0, 1.0, "AAL", capital=5000, simulation=False, name="AALTrendBot"),# 18425.99925114206, -1274.7570264960057, 0.7506112469437652, 818, 405, 413, 203
      TrendBot(4.0, 200, 36, 3.0, 1.0, "CTLT", capital=5000, simulation=False, name="CTLTTrendBot"),# 17549.390085353014, -754.9931844180035, 0.765625, 576, 312, 264, 134
      TrendBot(4.0, 80, 16, 3.0, 1.0, "DISH", capital=5000, simulation=False, name="DISHTrendBot"),# 17297.617115968034, -1836.0830295329952, 0.7544303797468355, 790, 374, 416, 193
      TrendBot(3.0, 60, 16, 2.0, 1.0, "TRMB", capital=5000, simulation=False, name="TRMBTrendBot"),# 15362.552755349012, -1.77169387, 0.7092307692307692, 650, 334, 316, 188
      #TrendBot(1.0, 40, 10, 3.0, 1.0, "PSX", capital=5000, simulation=False, name="PSXTrendBot"),# 15191.587751746063, -1.771745166, 0.7639639639639639, 555, 288, 267, 130
      #TrendBot(3.0, 80, 36, 3.0, 1.0, "META", capital=5000, simulation=False, name="METATrendBot"),# 14871.385643973004, -953.8884343579986, 0.7513321492007105, 563, 301, 
      ]

   print("waiting for market open")
   while(not IBInterface.market_open_in_secs(60*30)):
      time.sleep(10)
   log_name = "LiveUpdateProduction-" + str(datetime.datetime.today().strftime("%Y-%m-%d")) + ".txt"
   logging.basicConfig(filename=log_name, filemode='a', encoding='utf-8', level=logging.INFO)
   CapitalManager.initialize(11000, "live_capital.json")
   
   ip = "127.0.0.1"
   #ip = "192.168.50.138"
   port = 7497
   connection = 27

   interface = IBInterface(bot_pool)
   interface.after_market_enabled = False
   # print("Waiting for market to open")
   # while not interface.market_open_in_secs(10 * 60 * 60):
   #    time.sleep(5)
   # print("Market open in 10 minutes or already open")

   interface.start_bots(ip, port, connection, '10 mins', 1)

   while True:
      time.sleep(5)
      if not IBInterface.marketOpen() and not IBInterface.market_open_in_secs(60*31):
         time.sleep(30)
         print("Market closed")
         interface.disconnect()
         out_queue.put('q')
         break

      if not control_queue.empty():
         in_val = control_queue.get()
         if str(in_val) == 'q':
            print("Manual disconnect")
            interface.disconnect()
            break
         else:
            interface.closePosition(str(in_val))

if __name__ == "__main__":
   while True:
      console_queue = Queue()
      data_queue = Queue()
      prod_process = Process(target=production, args=(console_queue, data_queue), daemon=True)
      prod_process.start()
      val = None
      prod_val = None

      while True:
         #val = input("Enter q to quit or symbol to manually close:\n")
         #console_queue.put(val)
         if not data_queue.empty():
            prod_val = data_queue.get()
         if val == 'q' or prod_val == 'q':
            time.sleep(10)
            break
         time.sleep(5)
      
      prod_process.join()
      if val == 'q':
         break
