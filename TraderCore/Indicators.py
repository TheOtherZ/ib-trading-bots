from ibapi.wrapper import BarData
import TraderCore.HelperFunctions as hf

BarList = list[BarData]

class IndicatorBase(object):
   def __init__(self) -> None:
      pass

   def reset(self):
      pass

class EZVolume(IndicatorBase):
   def __init__(self, period) -> None:
      super().__init__()
      self.period = period
      self.gain_volume_list = [0] * self.period
      self.loss_volume_list = [0] * self.period

   def compute(self, last_bar: BarData):
      if last_bar.open < last_bar.close:
         change = last_bar.close - last_bar.open
         self.gain_volume_list.append(last_bar.volume / change)
         self.loss_volume_list.append(0)
         self.loss_volume_list.pop(0)
         self.gain_volume_list.pop(0)
      elif last_bar.open > last_bar.close:
         change = last_bar.open - last_bar.close
         self.gain_volume_list.append(0)
         self.loss_volume_list.append(last_bar.volume / change)
         self.loss_volume_list.pop(0)
         self.gain_volume_list.pop(0)

      avg_gain = sum(self.gain_volume_list) / self.period
      avg_loss = sum(self.loss_volume_list) / self.period

      if avg_loss == 0:
         self.value = 100
      else:
         gl_ratio = avg_gain / avg_loss

         self.value = 100 - (100 / (1 + gl_ratio))

      return self.value

class StochasticOscillator(IndicatorBase):
   def __init__(self, fast_window_size: int, slow_window_size: int) -> None:
      self.stochastic_window_size = fast_window_size
      self.slow_stochastic_window_size = slow_window_size
      self.min_window = [10000] * self.stochastic_window_size
      self.max_window = [0] * self.stochastic_window_size
      self.stochastic_values = [0] * self.slow_stochastic_window_size

      self.fast_value = 0
      self.slow_value = 0

   def compute(self, last_bar: BarData) -> tuple:
      self.min_window.append(last_bar.low)
      self.min_window.pop(0)
      self.max_window.append(last_bar.high)
      self.max_window.pop(0)
      min_val = min(self.min_window)
      max_val = max(self.max_window)

      if max_val - min_val != 0:
         self.fast_value = (last_bar.close - min_val) / (max_val - min_val) * 100
      self.stochastic_values.append( self.fast_value)
      self.stochastic_values.pop(0)

      self.slow_value = sum(self.stochastic_values) / len(self.stochastic_values)

      return self.fast_value, self.slow_value

class VolumeRSIOscillator(IndicatorBase):
   def __init__(self, period) -> None:
      self.period = period
      self.gain_volume_list = [0] * self.period
      self.loss_volume_list = [0] * self.period
      self.value = 0
   
   def compute(self, last_bar: BarData):
      if last_bar.open < last_bar.close:
         self.gain_volume_list.append(last_bar.volume)
         self.loss_volume_list.append(0)
         self.loss_volume_list.pop(0)
         self.gain_volume_list.pop(0)
      elif last_bar.open > last_bar.close:
         self.gain_volume_list.append(0)
         self.loss_volume_list.append(last_bar.volume)
         self.loss_volume_list.pop(0)
         self.gain_volume_list.pop(0)

      if sum(self.loss_volume_list) + sum(self.gain_volume_list) > 0:
         self.value = (sum(self.gain_volume_list) / (sum(self.loss_volume_list) + sum(self.gain_volume_list))) * 100
      else:
         self.value = 50

      return self.value

class RSIOscillator(IndicatorBase):
   def __init__(self, period) -> None:
      self.period = period
      self.gain_list = [0] * self.period
      self.loss_list = [0] * self.period
      self.last_avg_gain = 0
      self.last_avg_loss = 0
      self.value = 50
      self.total_count = 0

   def compute(self, last_bar: BarData):
      if last_bar.open < last_bar.close:
         self.gain_list.append(last_bar.close - last_bar.open)
         self.loss_list.append(0)
         self.loss_list.pop(0)
         self.gain_list.pop(0)
      elif last_bar.open > last_bar.close:
         self.gain_list.append(0)
         self.loss_list.append(last_bar.open - last_bar.close)
         self.loss_list.pop(0)
         self.gain_list.pop(0)
      
      self.total_count += 1
      if self.total_count < self.period - 1:
         return
      elif self.total_count == self.period:
         avg_gain = sum(self.gain_list) / self.period
         avg_loss = sum(self.loss_list) / self.period
      else:
         avg_gain = (self.last_avg_gain * (self.period - 1) + self.gain_list[-1]) / self.period
         avg_loss = (self.last_avg_loss * (self.period - 1) + self.loss_list[-1]) / self.period

      self.last_avg_gain = avg_gain
      self.last_avg_loss = avg_loss

      if avg_loss == 0:
         self.value = 100
      else:
         gl_ratio = avg_gain / avg_loss

         self.value = 100 - (100 / (1 + gl_ratio))

      return self.value

   def reset(self):
      self.total_count = 0


class MovingAverage(IndicatorBase):
   def __init__(self, window_size) -> None:
      self.window_size = window_size

   def compute(self, bar_list: BarList):
      val_sum = 0
      for bar in bar_list[-self.window_size:]:
         val_sum += bar.wap
      
      self.value = val_sum / self.window_size

      return self.value

   def compute_simple(self, val_list):
      val_sum = 0
      for val in val_list[-self.window_size:]:
         val_sum += val
      
      self.value = val_sum / self.window_size

      return self.value


class Derivative(IndicatorBase):
   def __init__(self, smoothing) -> None:
      super().__init__()
      self.smoothing = smoothing
      self.value_list = [0] * smoothing
      self.last_value = 0

   def compute(self, new_value):
      diff = new_value - self.last_value
      self.last_value = new_value
      self.value_list.append(diff)
      self.value_list.pop(0)

      self.value = sum(self.value_list) / self.smoothing

      return self.value


class CrossingMomentum(IndicatorBase):
   def __init__(self, crossing_count) -> None:
      super().__init__()
      self.crossing_count = crossing_count
      self.crossing_list = [0] * self.crossing_count
      self.crossing_value = 0
      self.value = 0

   def compute(self, moving_avg: float, last_bar: BarData):
      if last_bar.wap > moving_avg:
         self.crossing_list.append(1)
         self.crossing_list.pop(0)
      elif last_bar.wap < moving_avg:
         self.crossing_list.append(-1)
         self.crossing_list.pop(0)

      self.value = sum(self.crossing_list) / self.crossing_count

      return self.value
   
class MovingMass(IndicatorBase):
   def __init__(self, window_size) -> None:
      super().__init__()
      self.mass_window_size = window_size
      self.mass_window = [0] * self.window_size
      self.crossing_value = 0
      self.value = 0

   def compute(self, moving_avg: float, last_bar: BarData):
      if last_bar.wap > moving_avg:
         self.crossing_list.append(1)
         self.crossing_list.pop(0)
      elif last_bar.wap < moving_avg:
         self.crossing_list.append(-1)
         self.crossing_list.pop(0)

      self.value = sum(self.crossing_list) / self.crossing_count

      return self.value

class BenchmarkDeviation(IndicatorBase):
   def __init__(self) -> None:
      super().__init__()

   @staticmethod
   def compute(benchmark_bar: BarData, target_bar: BarData):
      benchmark_percent_change = (benchmark_bar.close - benchmark_bar.open) / benchmark_bar.open * 100
      target_percent_change = (target_bar.close - target_bar.open) / target_bar.open * 100

      return benchmark_percent_change - target_percent_change

if __name__ == "__main__":
   test_file = "Data/QQQ_Apr-25-2022-13-00.csv"

   bars = []
   with open(test_file, 'r') as t_file:
      count = 0
      for line in t_file.readlines():
         if count > 0: # Strip off header
            bars.append(hf.make_bar(*list(line.split(","))))
         count += 1

   rsi = RSIOscillator(100)
   rsi_volume = VolumeRSIOscillator(14)
   ez_volume = EZVolume(100)

   for bar in bars:
      rsi.compute(bar)
      rsi_volume.compute(bar)
      ez_volume.compute(bar)
      print(ez_volume.value)
   