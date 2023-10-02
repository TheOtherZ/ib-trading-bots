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
      TrendBot(3.0, 200, 36, 2.0, 1.0, "EPAM", capital=5000, simulation=False, name="EPAMTrendBot"),# 29878.210503528986, -1251.371551998993, 0.6022099447513812, 362, 183, 179, 143
      #TrendBot(1.0, 60, 24, 3.0, 2.0, "DISH", capital=5000, simulation=False, name="DISHTrendBot"),# 28526.128198269973, -1581.1008376240072, 0.6263345195729537, 281, 145, 136, 104
      TrendBot(1.0, 40, 24, 2.0, 1.0, "AMD", capital=5000, simulation=False, name="AMDTrendBot"),# 24672.209800031043, -868.545210940998, 0.6260296540362438, 607, 312, 295, 226
      TrendBot(4.0, 80, 24, 3.0, 2.0, "ETSY", capital=5000, simulation=False, name="ETSYTrendBot"),# 24029.039467935036, -552.479452119, 0.5857843137254902, 408, 205, 203, 168
      TrendBot(3.0, 40, 24, 3.0, 2.0, "TSLA", capital=5000, simulation=False, name="TSLATrendBot"),# 23189.814328369346, -626.1506396085229, 0.5985576923076923, 416, 208, 208, 166
      TrendBot(4.0, 60, 24, 3.0, 3.0, "NVDA", capital=5000, simulation=False, name="NVDATrendBot"),# 21653.423849827752, -1699.4211564739996, 0.55, 280, 146, 134, 125
      TrendBot(1.0, 80, 16, 3.0, 1.0, "F", capital=5000, simulation=False, name="FTrendBot"),# 21146.173582791977, -1595.0310907840003, 0.6868131868131868, 364, 178, 186, 113
      TrendBot(2.0, 80, 16, 3.0, 1.0, "CDNS", capital=5000, simulation=False, name="CDNSTrendBot"),# 21003.065503829966, -241.11799125599904, 0.7424749163879598, 299, 146, 153, 76
      # TrendBot(1.0, 40, 10, 3.0, 1.0, "META", capital=5000, simulation=False, name="METATrendBot"),# 20717.83948357998, -1.77436401, 0.7044198895027625, 362, 185, 177, 106
      # TrendBot(1.0, 40, 16, 3.0, 3.0, "TER", capital=5000, simulation=False, name="TERTrendBot"),# 20697.40556529702, -1182.7585544269948, 0.5726495726495726, 234, 120, 114, 99
      
      MeanRegressionBotLive(120, 80, 10, 4.0, 8, 3.0, "ALGN", 5000, simulation=False, name="ALGNRegressionBot"),# 12938.32200592398, -1.668166176, 0.7758620689655172, 58, 25, 33, 10
      MeanRegressionBotLive(120, 120, 10, 3.0, 8, 5.0, "LW", 5000, simulation=False, name="LWRegressionBot"),# 11871.847368757011, -1.6577755299999999, 0.7402597402597403, 77, 41, 36, 14
      MeanRegressionBotLive(80, 120, 10, 4.0, 8, 3.0, "WELL", 5000, simulation=False, name="WELLRegressionBot"),# 10811.482140373006, -1.7242324960000004, 0.78, 100, 59, 41, 8
      MeanRegressionBotLive(60, 120, 10, 4.0, 8, 5.0, "DXCM", 5000, simulation=False, name="DXCMRegressionBot"),# 10596.400647368991, -783.3847850272485, 0.7102803738317757, 107, 58, 49, 22
      MeanRegressionBotLive(80, 80, 10, 3.0, 8, 2.0, "EXPE", 5000, simulation=False, name="EXPERegressionBot"),# 10583.320283174997, -1650.2707002920022, 0.7142857142857143, 77, 35, 42, 19
      MeanRegressionBotLive(60, 120, 10, 3.0, 8, 2.0, "NCLH", 5000, simulation=False, name="NCLHRegressionBot"),# 10333.263231181983, -483.6373737619998, 0.6724137931034483, 116, 45, 71, 36
      MeanRegressionBotLive(150, 60, 10, 2.0, 8, 3.0, "WBD", 5000, simulation=False, name="WBDRegressionBot"),# 10313.01846699, -5.227040000000001, 0.6896551724137931, 29, 10, 19, 8
      MeanRegressionBotLive(150, 80, 10, 4.0, 8, 3.0, "PFE", 5000, simulation=False, name="PFERegressionBot"),# 10309.594468736983, -10.5546, 0.7916666666666666, 48, 23, 25, 4
      #MeanRegressionBotLive(200, 120, 10, 4.0, 8, 5.0, "NVDA", 5000, simulation=False, name="NVDARegressionBot"),# 10286.583232947258, -661.0869945975006, 0.673469387755102, 49, 23, 26, 13
      MeanRegressionBotLive(80, 80, 10, 3.0, 8, 4.0, "MPWR", 5000, simulation=False, name="MPWRRegressionBot"),# 9914.119908540993, -406.295168525, 0.6538461538461539, 78, 50, 28, 25
      MeanRegressionBotLive(200, 120, 16, 4.0, 8, 5.0, "HAL", 5000, simulation=False, name="HALRegressionBot"),# 9673.963154045, -383.8772061010018, 0.7419354838709677, 31, 17, 14, 7
      MeanRegressionBotLive(200, 120, 16, 4.0, 8, 5.0, "DPZ", 5000, simulation=False, name="DPZRegressionBot"),# 9650.722862932009, -1.82, 0.8285714285714286, 35, 20, 15, 4
      MeanRegressionBotLive(60, 120, 10, 3.0, 8, 5.0, "NRG", 5000, simulation=False, name="NRGRegressionBot"),# 9403.49786954501, -480.4942929879986, 0.7572815533980582, 103, 56, 47, 22
      #MeanRegressionBotLive(120, 120, 16, 4.0, 8, 2.0, "AOS", 5000, simulation=False, name="AOSRegressionBot"),# 9241.961966162, -5.65425, 0.8936170212765957, 47, 25, 22, 3
      #MeanRegressionBotLive(60, 120, 10, 4.0, 8, 2.0, "SO", 5000, simulation=False, name="SORegressionBot"),# 9127.388680469987, -189.34941527499927, 0.7413793103448276, 116, 66, 50, 4
      #MeanRegressionBotLive(150, 120, 10, 4.0, 8, 5.0, "DOV", 5000, simulation=False, name="DOVRegressionBot"),# 9067.869686005011, -3.22, 0.8360655737704918, 61, 32, 29, 6
      #MeanRegressionBotLive(80, 80, 10, 4.0, 8, 5.0, "ISRG", 5000, simulation=False, name="ISRGRegressionBot"),# 9067.160620523828, -749.1791992534286, 0.7662337662337663, 77, 42, 35, 12
      #MeanRegressionBotLive(120, 120, 10, 4.0, 8, 4.0, "AVGO", 5000, simulation=False, name="AVGORegressionBot"),# 8942.974086934017, -1.653407584, 0.7571428571428571, 70, 43, 27, 9
      #MeanRegressionBotLive(120, 120, 10, 4.0, 8, 4.0, "CBOE", 5000, simulation=False, name="CBOERegressionBot"),# 8848.677320263994, -1.6568668579999999, 0.7857142857142857, 70, 38, 32, 6
      #MeanRegressionBotLive(120, 120, 10, 2.0, 8, 2.0, "GM", 5000, simulation=False, name="GMRegressionBot"),# 8790.482496845016, -298.6630754099976, 0.6575342465753424, 73, 36, 37, 25
      #MeanRegressionBotLive(150, 80, 10, 4.0, 8, 5.0, "CZR", 5000, simulation=False, name="CZRRegressionBot"),# 8705.289335704001, -1.6572850119999996, 0.7441860465116279, 43, 19, 24, 11
      #MeanRegressionBotLive(150, 120, 10, 4.0, 8, 4.0, "CF", 5000, simulation=False, name="CFRegressionBot"),# 8699.583552950005, -978.1497299959999, 0.7169811320754716, 53, 27, 26, 13
      #MeanRegressionBotLive(80, 120, 16, 4.0, 8, 5.0, "STLD", 5000, simulation=False, name="STLDRegressionBot"),# 8678.764580915016, -685.3898139819956, 0.6885245901639344, 61, 36, 25, 13
      #MeanRegressionBotLive(60, 120, 10, 4.0, 8, 3.0, "XEL", 5000, simulation=False, name="XELRegressionBot"),# 8651.499853897029, -6.00607, 0.7410714285714286, 112, 59, 53, 5
      #MeanRegressionBotLive(60, 120, 10, 4.0, 8, 2.0, "KEY", 5000, simulation=False, name="KEYRegressionBot"),# 8602.019648634994, -18.14386, 0.696078431372549, 102, 50, 52, 12
      #MeanRegressionBotLive(200, 120, 16, 4.0, 8, 5.0, "F", 5000, simulation=False, name="FRegressionBot"),# 8436.057788739003, -1511.4470598249968, 0.65, 40, 17, 23, 11
      #MeanRegressionBotLive(120, 120, 10, 4.0, 8, 4.0, "VTR", 5000, simulation=False, name="VTRRegressionBot"),# 8387.191370731987, -2.062775856, 0.7567567567567568, 74, 37, 37, 9
      #MeanRegressionBotLive(150, 80, 10, 4.0, 8, 5.0, "TROW", 5000, simulation=False, name="TROWRegressionBot"),# 8359.876787565003, -54.81664701800095, 0.7659574468085106, 47, 21, 26, 7
      #MeanRegressionBotLive(80, 120, 10, 4.0, 8, 3.0, "SNPS", 5000, simulation=False, name="SNPSRegressionBot"),# 8333.549315225007, -2.3, 0.7142857142857143, 91, 51, 40, 16
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
