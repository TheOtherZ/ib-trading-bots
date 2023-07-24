import logging
import datetime
import time
from multiprocessing import Queue, Process
from LiveCore.CapitalManager import CapitalManager
from LiveCore.LiveIBInterface import IBInterface
from TrendBot import TrendBot

def production(control_queue: Queue, out_queue: Queue):
   bot_pool = [
      TrendBot(1.0, 200, 36, 3.0, 1.0, "EPAM", capital=5000, simulation=False, name="EPAMTrendBot"),# 28891.919180187953, -79.90057475300006, 0.7571606475716065, 803, 436, 367, 194
      TrendBot(3.0, 40, 24, 3.0, 1.0, "RCL", capital=5000, simulation=False, name="RCLTrendBot"),# 23104.601400981042, -1446.6853098429785, 0.7437020810514786, 913, 459, 454, 233
      TrendBot(2.0, 80, 10, 3.0, 1.0, "ETSY", capital=5000, simulation=False, name="ETSYTrendBot"),# 22717.708481326983, -4926.9851986860085, 0.7414548641542507, 1141, 566, 575, 294
      TrendBot(1.0, 60, 16, 3.0, 1.0, "FTNT", capital=5000, simulation=False, name="FTNTTrendBot"),# 18913.405885482156, -1322.791760194201, 0.7539797395079595, 691, 363, 328, 169
      TrendBot(4.0, 60, 16, 3.0, 1.0, "AAL", capital=5000, simulation=False, name="AALTrendBot"),# 18425.99925114206, -1274.7570264960057, 0.7506112469437652, 818, 405, 413, 203
      TrendBot(4.0, 200, 36, 3.0, 1.0, "CTLT", capital=5000, simulation=False, name="CTLTTrendBot"),# 17549.390085353014, -754.9931844180035, 0.765625, 576, 312, 264, 134
      TrendBot(4.0, 80, 16, 3.0, 1.0, "DISH", capital=5000, simulation=False, name="DISHTrendBot"),# 17297.617115968034, -1836.0830295329952, 0.7544303797468355, 790, 374, 416, 193
      TrendBot(3.0, 60, 16, 2.0, 1.0, "TRMB", capital=5000, simulation=False, name="TRMBTrendBot"),# 15362.552755349012, -1.77169387, 0.7092307692307692, 650, 334, 316, 188
      TrendBot(1.0, 40, 10, 3.0, 1.0, "PSX", capital=5000, simulation=False, name="PSXTrendBot"),# 15191.587751746063, -1.771745166, 0.7639639639639639, 555, 288, 267, 130
      TrendBot(3.0, 80, 36, 3.0, 1.0, "META", capital=5000, simulation=False, name="METATrendBot"),# 14871.385643973004, -953.8884343579986, 0.7513321492007105, 563, 301, 
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
