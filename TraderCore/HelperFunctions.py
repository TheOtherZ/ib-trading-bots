from audioop import mul
from ibapi.wrapper import BarData

BarList = list[BarData]

def make_bar(date, open, high, low, close, volume, average, barCount):
   new_bar = BarData()
   new_bar.date = str(date)
   new_bar.open = float(open)
   new_bar.high = float(high)
   new_bar.low = float(low)
   new_bar.close = float(close)
   new_bar.volume = int(float(volume))
   new_bar.wap = float(average)
   new_bar.barCount = int(barCount)

   return new_bar

def make_bar_string(bar: BarData):
   return "%s,%s,%s,%s,%s,%s,%s,%s" % (bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume, bar.wap, bar.barCount)

def upscale_bars(bar_list: BarList) -> BarData:
   open = bar_list[0].open
   close = bar_list[-1].close

   max_val = 0
   min_val = 100000
   avg = 0
   volume = 0
   bar_count = 0
   for bar in bar_list:
      max_val = bar.high if bar.high > max_val else max_val
      min_val =  bar.low if bar.low < min_val else min_val
      avg += bar.wap
      volume += bar.volume
      bar_count += bar.barCount

   avg = avg / len(bar_list)

   return make_bar(bar_list[0].date, open, max_val, min_val, close, volume, avg, bar_count)

def upscale_file(file_name: str, output_file, multiple):
   with open(file_name, 'r') as base_file:
      new_lines = []
      x = 0
      combined_bars = []
      for line in base_file.readlines():
         if x == 0:
            new_lines.append(line) #column headers
         elif x % multiple == 0:
            combined_bars.append(make_bar(*list(line.split(","))))
            new_bar = upscale_bars(combined_bars)
            new_lines.append(make_bar_string(new_bar) + "\n")
            combined_bars = []
         else:
            combined_bars.append(make_bar(*list(line.split(","))))
         
         x += 1

      with open(output_file, 'w') as out_file:
         out_file.writelines(new_lines)
         

def create_master_file_list(master_file_list):
   u_file_names = []
   s_file_names = []
   l_file_names = []

   tick = 0
   with open(master_file_list, 'r') as file_list_file:
      for filename in file_list_file.readlines():
         tick += 1
         if tick == 1:
            u_file_names.append(filename.strip('\n'))
         elif tick == 2:
            s_file_names.append(filename.strip('\n'))
         elif tick == 3:
            l_file_names.append(filename.strip('\n'))
            tick = 0

   master_list = []
   for i, _ in enumerate(u_file_names):
      underlying_file = u_file_names[i - len(u_file_names)]
      short_file = s_file_names[i - len(u_file_names)]
      long_file = l_file_names[i - len(u_file_names)]
      master_list.append((underlying_file, short_file, long_file))
   
   return master_list

if __name__ == "__main__":
   master_name = "Data2/historic_data_list.txt"
   out_dir = "Upscale1Sec/"
   new_master_name = out_dir + "historic_data_list.txt"

   master_file_list = create_master_file_list(master_name)

   with open(new_master_name, 'w') as new_master_list:
      for item in master_file_list:
         for name in item:
            new_name = out_dir + name.split("/")[1]
            new_master_list.write(new_name + "\n")
            upscale_file(name, new_name, 2)
