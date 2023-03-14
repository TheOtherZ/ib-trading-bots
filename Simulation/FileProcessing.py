import TraderCore.HelperFunctions as hf

from ibapi.wrapper import BarData

def convert_bar_file(bar_file_name: str):
   bars = []
   period_size = 0
   with open(bar_file_name, 'r') as bar_file:
      # Strip off column headers
      period_size = len(list(bar_file.readline().split(",")))
      for line in bar_file.readlines():
         bars.append(hf.make_bar(*list(line.split(","))))
   
   return bars, period_size

def make_flat_bars_from_master(master_file_name, data_dir):
   flat_bars = []
   with open(data_dir + master_file_name, 'r') as master_file:
      for bar_file_name in master_file.readlines():
         bars, size = convert_bar_file(data_dir + bar_file_name.strip('\n'))
         # if size != period_size:
         #    raise ValueError("Incorrect data size, expected: %s but got: %s for file: %s" % (period_size, size, bar_file_name))
         flat_bars += bars
   
   return flat_bars