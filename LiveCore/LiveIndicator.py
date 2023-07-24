from ibapi.wrapper import BarData

class MovingAverage(object):
   def __init__(self, window_size) -> None:
      self.window_size = window_size

   def compute(self, bar_list: list[BarData]):
      val_sum = 0
      for bar in bar_list[-self.window_size:]:
         val_sum += float(bar.wap)
      
      self.value = val_sum / self.window_size

      return self.value
   
class ValMovingAverage(object):
   def __init__(self, window_size) -> None:
      self.window_size = window_size
      self.value = 0

   def compute(self, val_list: list[float]):
      val_sum = 0
      for val in val_list[-self.window_size:]:
         val_sum += float(val)
      
      self.value = val_sum / float(self.window_size)

      return self.value
   
class RSIOscillator(object):
   def __init__(self, period) -> None:
      self.period = period
      self.gain_list = [0] * self.period
      self.loss_list = [0] * self.period
      self.last_avg_gain = 0
      self.last_avg_loss = 0
      self.value = 50
      self.total_count = 0

      self.live = False
      self.last_processed_bar = BarData()
      self.last_completed_bar = BarData()
      self.last_processed_gain = 0
      self.last_processed_loss = 0

   def compute(self, last_bar: BarData, bar_started=True):        

      if bar_started:
         self.total_count += 1
         diff = last_bar.close - last_bar.open
         if diff > 0:
            self.gain_list.append(diff)
            self.loss_list.append(0)
            self.loss_list.pop(0)
            self.gain_list.pop(0)
         elif diff < 0:
            self.gain_list.append(0)
            self.loss_list.append(-diff)
            self.loss_list.pop(0)
            self.gain_list.pop(0)
         
         self.last_completed_bar = last_bar
      # Streaming data
      elif self.live:
         diff = last_bar.close - self.last_completed_bar.close
         if diff > 0:
            self.gain_list[-1] = diff
            self.loss_list[-1] = 0
         elif diff < 0:
            self.gain_list[-1] = 0
            self.loss_list[-1] = -diff

      self.last_processed_bar = last_bar

      if bar_started and self.live:
         self.last_avg_gain = self.last_processed_gain
         self.last_avg_loss = self.last_processed_loss

      if self.total_count < self.period - 1:
         return
      elif self.total_count == self.period:
         avg_gain = sum(self.gain_list) / self.period
         avg_loss = sum(self.loss_list) / self.period
      else:
         avg_gain = (self.last_avg_gain * (self.period - 1) + self.gain_list[-1]) / self.period
         avg_loss = (self.last_avg_loss * (self.period - 1) + self.loss_list[-1]) / self.period

      self.last_processed_gain = avg_gain
      self.last_processed_loss = avg_loss

      if bar_started and not self.live:
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

class RSIOscillator2(object):
   def __init__(self, period, live=False) -> None:
      self.period = period
      self.gain_list = [0] * self.period
      self.loss_list = [0] * self.period
      self.live = live
      self.last_avg_gain = 0
      self.last_avg_loss = 0
      self.value = 50
      self.total_count = 0
      self.last_complete_bar = None
      self.last_bar_processed = None

   def compute(self, last_bar: BarData, new_bar: bool=False):
      if self.last_complete_bar == None:
         self.last_complete_bar = last_bar
         self.last_bar_processed = last_bar
         return
        
      if new_bar:
         # Last bar was final bar for period
         diff = self.last_bar_processed.close - self.last_bar_processed.open
         self.last_complete_bar = self.last_bar_processed
         live_dif = last_bar.close - self.last_complete_bar.close
         if self.live:
            if diff > 0:
               self.gain_list[-1] = diff
               self.loss_list[-1] = 0
            elif diff < 0:
               self.gain_list[-1] = 0
               self.loss_list[-1] = -diff

            if live_dif > 0:
               self.gain_list.append(live_dif)
               self.loss_list.append(0)
               self.loss_list.pop(0)
               self.gain_list.pop(0)
            elif live_dif < 0:
               self.gain_list.append(0)
               self.loss_list.append(-live_dif)
               self.loss_list.pop(0)
               self.gain_list.pop(0)
         else:
            #diff = last_bar.close - last_bar.open
            if diff > 0:
               self.gain_list.append(diff)
               self.loss_list.append(0)
               self.loss_list.pop(0)
               self.gain_list.pop(0)
            elif diff < 0:
               self.gain_list.append(0)
               self.loss_list.append(-diff)
               self.loss_list.pop(0)
               self.gain_list.pop(0)

         self.total_count += 1
      else:
         diff = last_bar.close - self.last_complete_bar.close
         if diff > 0:
            self.gain_list[-1] = diff
            self.loss_list[-1] = 0
         elif diff < 0:
            self.gain_list[-1] = 0
            self.loss_list[-1] = -diff
      
      self.last_bar_processed = last_bar

      if self.total_count < self.period - 1:
         return
      elif self.total_count == self.period:
         avg_gain = sum(self.gain_list) / self.period
         avg_loss = sum(self.loss_list) / self.period
      else:
         avg_gain = (self.last_avg_gain * (self.period - 1) + self.gain_list[-1]) / self.period
         avg_loss = (self.last_avg_loss * (self.period - 1) + self.loss_list[-1]) / self.period

      if new_bar:
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

class MovingMass(object):
   def __init__(self, window_size) -> None:
      super().__init__()
      self.mass_window_size = window_size
      self.above_window = [0] * self.mass_window_size
      self.below_window = [0] * self.mass_window_size
      self.last_avg_above = 0
      self.last_avg_below = 0
      self.value = 50
      self.total_count = 0

   def compute(self, moving_avg: float, last_bar: BarData, new_bar_started: bool):
      diff = float(last_bar.wap) - moving_avg
      if new_bar_started:
         if diff >= 0:
            self.above_window.append(diff)
            self.below_window.append(0)
         else:
            self.above_window.append(0)
            self.below_window.append(-diff)
         
         self.above_window.pop(0)
         self.below_window.pop(0)
         self.total_count += 1
      else:
         if diff >= 0:
            self.above_window[-1] = diff
            self.below_window[-1] = 0
         else:
            self.above_window[-1] = 0
            self.below_window[-1] = -diff

      if self.total_count < self.mass_window_size - 1:
         return self.value
      elif self.total_count == self.mass_window_size:
         avg_above = sum(self.above_window) / self.mass_window_size
         avg_below = sum(self.below_window) / self.mass_window_size
      else:
         avg_above = (self.last_avg_above * (self.mass_window_size - 1) + self.above_window[-1]) / self.mass_window_size
         avg_below = (self.last_avg_below * (self.mass_window_size - 1) + self.below_window[-1]) / self.mass_window_size

      if new_bar_started:
         self.last_avg_above = avg_above
         self.last_avg_below = avg_below
      if avg_below == 0:
         self.value = 100
      else:
         ratio = avg_above / avg_below
         self.value = 100 - (100 / (1 + ratio))

      return self.value