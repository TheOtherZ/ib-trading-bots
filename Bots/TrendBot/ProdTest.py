import logging
import datetime
import time
from multiprocessing import Queue, Process
from LiveCore.CapitalManager import CapitalManager
from LiveCore.LiveIBInterface import IBInterface
from TrendBot import TrendBot

def production(control_queue: Queue, out_queue: Queue):
   bot_pool = [      
      TrendBot(3.0, 200, 36, 2.0, 1.0, "EPAM", capital=5000, simulation=False, name="EPAMTrendBot"),# 29878.210503528986, -1251.371551998993, 0.6022099447513812, 362, 183, 179, 143
      TrendBot(1.0, 60, 24, 3.0, 2.0, "DISH", capital=5000, simulation=False, name="DISHTrendBot"),# 28526.128198269973, -1581.1008376240072, 0.6263345195729537, 281, 145, 136, 104
      TrendBot(1.0, 40, 24, 2.0, 1.0, "AMD", capital=5000, simulation=False, name="AMDTrendBot"),# 24672.209800031043, -868.545210940998, 0.6260296540362438, 607, 312, 295, 226
      TrendBot(4.0, 80, 24, 3.0, 2.0, "ETSY", capital=5000, simulation=False, name="ETSYTrendBot"),# 24029.039467935036, -552.479452119, 0.5857843137254902, 408, 205, 203, 168
      TrendBot(3.0, 40, 24, 3.0, 2.0, "TSLA", capital=5000, simulation=False, name="TSLATrendBot"),# 23189.814328369346, -626.1506396085229, 0.5985576923076923, 416, 208, 208, 166
      TrendBot(4.0, 60, 24, 3.0, 3.0, "NVDA", capital=5000, simulation=False, name="NVDATrendBot"),# 21653.423849827752, -1699.4211564739996, 0.55, 280, 146, 134, 125
      TrendBot(1.0, 80, 16, 3.0, 1.0, "F", capital=5000, simulation=False, name="FTrendBot"),# 21146.173582791977, -1595.0310907840003, 0.6868131868131868, 364, 178, 186, 113
      TrendBot(2.0, 80, 16, 3.0, 1.0, "CDNS", capital=5000, simulation=False, name="CDNSTrendBot"),# 21003.065503829966, -241.11799125599904, 0.7424749163879598, 299, 146, 153, 76
      TrendBot(1.0, 40, 10, 3.0, 1.0, "META", capital=5000, simulation=False, name="METATrendBot"),# 20717.83948357998, -1.77436401, 0.7044198895027625, 362, 185, 177, 106
      TrendBot(1.0, 40, 16, 3.0, 3.0, "TER", capital=5000, simulation=False, name="TERTrendBot"),# 20697.40556529702, -1182.7585544269948, 0.5726495726495726, 234, 120, 114, 99
      ]

   print("waiting for market open")
   while(not IBInterface.market_open_in_secs(60*30)):
      time.sleep(10)
   log_name = "LiveUpdateProduction-" + str(datetime.datetime.today().strftime("%Y-%m-%d")) + ".txt"
   logging.basicConfig(filename=log_name, filemode='a', encoding='utf-8', level=logging.INFO)
   CapitalManager.initialize(31000, "live_capital.json")
   
   ip = "127.0.0.1"
   #ip = "192.168.50.138"
   port = 7498
   connection = 28

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
