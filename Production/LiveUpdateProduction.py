import logging
import datetime
import time
from multiprocessing import Queue, Process
from LiveCore.CapitalManager import CapitalManager
from LiveCore.LiveIBInterface import IBInterface
from Bots.MeanRegression.MeanRegressionBotLive import MeanRegressionBotLive

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
      MeanRegressionBotLive(80, 120, 10, 4.0, 8, 3.0, "FITB", 5000, simulation=False, name="FITBRegressionBot"),# 8273.273836258011, -9.876090000000001, 0.7010309278350515, 97, 50, 47, 14
      MeanRegressionBotLive(150, 120, 10, 4.0, 8, 2.0, "MCHP", 5000, simulation=False, name="MCHPRegressionBot"),# 8245.934864751021, -263.91650521250017, 0.7777777777777778, 63, 31, 32, 9
      MeanRegressionBotLive(60, 120, 10, 3.0, 8, 2.0, "PARA", 5000, simulation=False, name="PARARegressionBot"),# 8225.530643472, -510.6326359819981, 0.7008547008547008, 117, 46, 71, 31
      MeanRegressionBotLive(60, 80, 10, 4.0, 8, 3.0, "BA", 5000, simulation=False, name="BARegressionBot"),# 8223.055568900005, -1415.9623287449972, 0.65625, 96, 47, 49, 20
      MeanRegressionBotLive(150, 120, 10, 4.0, 8, 2.0, "BIIB", 5000, simulation=False, name="BIIBRegressionBot"),# 8173.081470214989, -217.72182638299796, 0.7903225806451613, 62, 31, 31, 9
      MeanRegressionBotLive(150, 120, 10, 3.0, 8, 2.0, "WYNN", 5000, simulation=False, name="WYNNRegressionBot"),# 8112.5197302809975, -814.7721072009975, 0.7164179104477612, 67, 31, 36, 18
      MeanRegressionBotLive(60, 120, 10, 3.0, 8, 2.0, "PPL", 5000, simulation=False, name="PPLRegressionBot"),# 8105.368263875002, -13.39429, 0.6964285714285714, 112, 59, 53, 7
      MeanRegressionBotLive(80, 40, 10, 4.0, 8, 2.0, "MRNA", 5000, simulation=False, name="MRNARegressionBot"),# 8103.597976522012, -3.14, 0.7586206896551724, 29, 15, 14, 6
      MeanRegressionBotLive(120, 120, 10, 2.0, 8, 5.0, "BLK", 5000, simulation=False, name="BLKRegressionBot"),# 8012.698938956023, -1.66160212, 0.7236842105263158, 76, 40, 36, 21
      MeanRegressionBotLive(60, 120, 16, 4.0, 8, 2.0, "EQT", 5000, simulation=False, name="EQTRegressionBot"),# 7998.971295539983, -4.73987466, 0.7580645161290323, 62, 35, 27, 13
      MeanRegressionBotLive(60, 120, 10, 4.0, 8, 4.0, "PEAK", 5000, simulation=False, name="PEAKRegressionBot"),# 7998.591764771997, -11.8111, 0.75, 108, 59, 49, 8
      MeanRegressionBotLive(80, 120, 24, 2.0, 8, 5.0, "TRMB", 5000, simulation=False, name="TRMBRegressionBot"),# 7989.467437844001, -321.9657166770015, 0.8620689655172413, 29, 14, 15, 3
      MeanRegressionBotLive(80, 120, 16, 4.0, 8, 2.0, "RF", 5000, simulation=False, name="RFRegressionBot"),# 7928.156276071003, -17.56587, 0.8478260869565217, 46, 28, 18, 3
      MeanRegressionBotLive(80, 120, 16, 4.0, 8, 5.0, "ADP", 5000, simulation=False, name="ADPRegressionBot"),# 7927.759091214008, -1331.2033070689981, 0.7457627118644068, 59, 35, 24, 4
      MeanRegressionBotLive(80, 80, 16, 4.0, 8, 3.0, "AON", 5000, simulation=False, name="AONRegressionBot"),# 7924.317266289006, -10.563986539998316, 0.8571428571428571, 35, 19, 16, 0
      MeanRegressionBotLive(200, 60, 10, 3.0, 8, 4.0, "DVA", 5000, simulation=False, name="DVARegressionBot"),# 7922.018571767997, -305.26949424700086, 0.8125, 32, 17, 15, 5
      MeanRegressionBotLive(80, 60, 10, 3.0, 8, 5.0, "ANET", 5000, simulation=False, name="ANETRegressionBot"),# 7894.846386686004, -5.25217, 0.8070175438596491, 57, 33, 24, 9
      MeanRegressionBotLive(80, 120, 10, 3.0, 8, 3.0, "JCI", 5000, simulation=False, name="JCIRegressionBot"),# 7891.240660710987, -1144.4143547770161, 0.7128712871287128, 101, 58, 43, 20
      MeanRegressionBotLive(60, 80, 10, 4.0, 8, 5.0, "BR", 5000, simulation=False, name="BRRegressionBot"),# 7854.284896901998, -3.08, 0.7708333333333334, 96, 55, 41, 5
      MeanRegressionBotLive(60, 120, 10, 3.0, 8, 4.0, "AME", 5000, simulation=False, name="AMERegressionBot"),# 7850.442389654019, -1.657235777, 0.7203389830508474, 118, 66, 52, 11
      MeanRegressionBotLive(80, 80, 16, 3.0, 8, 5.0, "MSCI", 5000, simulation=False, name="MSCIRegressionBot"),# 7845.661969918997, -1.6800000000000002, 0.8235294117647058, 34, 19, 15, 5
      MeanRegressionBotLive(120, 120, 10, 4.0, 8, 2.0, "VRTX", 5000, simulation=False, name="VRTXRegressionBot"),# 7716.83076999599, -252.01632539800266, 0.7532467532467533, 77, 41, 36, 7
      MeanRegressionBotLive(60, 120, 10, 3.0, 8, 5.0, "BKNG", 5000, simulation=False, name="BKNGRegressionBot"),# 7686.79212190002, -3117.5266785150006, 0.6756756756756757, 111, 66, 45, 30
      MeanRegressionBotLive(120, 120, 10, 3.0, 8, 4.0, "EVRG", 5000, simulation=False, name="EVRGRegressionBot"),# 7677.9148482050105, -6.43328, 0.8157894736842105, 76, 44, 32, 8
      MeanRegressionBotLive(120, 120, 10, 4.0, 8, 5.0, "PYPL", 5000, simulation=False, name="PYPLRegressionBot"),# 7625.540210774993, -1150.2127575770035, 0.6575342465753424, 73, 31, 42, 17
      MeanRegressionBotLive(80, 120, 10, 4.0, 8, 5.0, "MCO", 5000, simulation=False, name="MCORegressionBot"),# 7590.331118965006, -186.20105206199995, 0.7045454545454546, 88, 45, 43, 11
      MeanRegressionBotLive(120, 80, 10, 4.0, 8, 3.0, "JBHT", 5000, simulation=False, name="JBHTRegressionBot"),# 7578.408549390985, -1.6593865450000003, 0.7959183673469388, 49, 28, 21, 3
      MeanRegressionBotLive(80, 120, 16, 2.0, 8, 2.0, "IDXX", 5000, simulation=False, name="IDXXRegressionBot"),# 7494.554267429005, -11.772884363000854, 0.671875, 64, 34, 30, 20
      MeanRegressionBotLive(200, 120, 16, 4.0, 8, 3.0, "OXY", 5000, simulation=False, name="OXYRegressionBot"),# 7453.722499898999, -3.4575116020000003, 0.7058823529411765, 34, 20, 14, 9
      MeanRegressionBotLive(120, 120, 16, 4.0, 8, 5.0, "ANSS", 5000, simulation=False, name="ANSSRegressionBot"),# 7442.174653481999, -1.9, 0.7254901960784313, 51, 25, 26, 10
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
         console_queue.put(val)
         if not data_queue.empty():
            prod_val = data_queue.get()
         if val == 'q' or prod_val == 'q':
            time.sleep(10)
            break
         time.sleep(5)
      
      prod_process.join()
      if val == 'q':
         break
