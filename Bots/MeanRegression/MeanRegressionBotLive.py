import logging
logger = logging.getLogger(__name__)

from ibapi.wrapper import BarData

from LiveCore.LiveTraderBase import LiveTraderBase
from TraderCore.TradingCosts import ibkr_trading_costs, TradingCosts
import LiveCore.LiveIndicator as ind
from TraderCore.Indicators import RSIOscillator, MovingMass
from TraderCore.HelperFunctions import compute_percent_threshold


class MeanRegressionBotLive(LiveTraderBase):
   def __init__(self, average_window: int, momentum_window_long: int, momentum_window: int, stop_loss: float, rsi_window: int, profit_take: float, ticker: str, capital: float=15000.0, cost: TradingCosts=ibkr_trading_costs, simulation: bool = True, name: str = "none_bot") -> None:
      super().__init__(trading_costs=cost, name=name, simulation=simulation, capital=capital)

      self.ticker = ticker

      self.moving_average = ind.MovingAverage(average_window)
      self.long_mass = MovingMass(momentum_window_long)
      self.moving_mass = MovingMass(momentum_window)
      self.rsi = RSIOscillator(rsi_window)

      #TODO
      self.new_rsi = ind.RSIOscillator(rsi_window)
      self.new_long_mass = ind.MovingMass(momentum_window_long)
      self.new_moving_mass = ind.MovingMass(momentum_window)

      self.bar_list = []
      self.data_length = average_window + momentum_window_long + 5 #Some padding
      self.trade_active = False
      self.quantity_to_open = 1

      self.stop_loss = stop_loss
      self.proft_take = profit_take
      self.capital = capital
      
      self.last_bar = BarData()

   
   def process(self, bar: BarData, new_bar=False):
      if new_bar:
         if self.trading_enabled and not self.simulation:
            print("New Bar")
         self.bar_list.append(bar)
         if len(self.bar_list) > self.data_length:
            self.bar_list.pop(0)
            if not self.trade_active:
               logger.info(self.name + " Data fill complete, trading active for " + self.ticker)
            self.trade_active = True
         self.rsi.compute(self.last_bar)
      else:
         self.bar_list[-1] = bar

      self.moving_average.compute(self.bar_list)
      self.new_rsi.compute(bar, new_bar)

      self.quantity_to_open = self.compute_share_quantity(bar.close, self.capital)

      if len(self.bar_list) > self.moving_average.window_size:
         if new_bar:
            self.long_mass.compute(self.moving_average.value, self.last_bar)
            self.moving_mass.compute(self.moving_average.value, self.last_bar)
         self.new_long_mass.compute(self.moving_average.value, bar, new_bar)
         self.new_moving_mass.compute(self.moving_average.value, bar, new_bar)

      if self.trading_enabled and not self.simulation:
         print(f"{self.ticker}: CLOSE: {round(bar.close, 3)}, BARAVG: {round(bar.wap, 3)}, AVG: {round(self.moving_average.value, 3)}, RSI: {round(self.rsi.value, 2)} {round(self.new_rsi.value, 2)}, LONG: {round(self.long_mass.value, 2)} {round(self.new_long_mass.value, 2)}, SHORT: {round(self.moving_mass.value, 2)} {round(self.new_moving_mass.value, 2)}") #TODO
      
      self.last_bar = bar
      if not self.trade_active:
         return 0
      #TODO
      # open_long = self.moving_mass.value < 8 and bar.close < self.moving_average.value and self.rsi.value < 20
      # open_short = self.moving_mass.value > 92 and bar.close > self.moving_average.value and self.rsi.value > 80
      open_long = self.moving_mass.value < 15 and bar.close < self.moving_average.value and self.rsi.value < 20 and self.long_mass.value > 70
      open_short = self.moving_mass.value > 85 and bar.close > self.moving_average.value and self.rsi.value > 80 and self.long_mass.value < 30
      # open_long = self.moving_mass.value < 15 and bar.close < self.moving_average.value and self.long_mass.value > 75
      # open_short = self.moving_mass.value > 85 and bar.close > self.moving_average.value and self.long_mass.value < 25
      
      if self.num_held == 0:
         if open_long:
            self.order(bar.close, self.quantity_to_open)
         elif open_short:
            self.order(bar.close, -self.quantity_to_open)

      else:
         stop_long = False
         stop_short = False
         stop_short, stop_long = compute_percent_threshold(self.average_price, bar.close, self.stop_loss)
         profit_long, profit_short = compute_percent_threshold(self.average_price, bar.close, self.proft_take)


         close = False
         if self.num_held > 0 and (stop_long or self.moving_mass.value > 85 or profit_long):
            if stop_long:
               self.stop_trades += 1
            close = True
         elif self.num_held < 0 and (stop_short or self.moving_mass.value < 15 or profit_short):
            if stop_short:
               self.stop_trades += 1
            close = True
         
         if close:
            self.order(bar.close, -self.num_held)

      return super().process()
   
   def confirm_order(self, price: float, quantity: int):
      return super().confirm_order(price, quantity)

   def get_parameters(self):
      return self.moving_average.window_size, self.long_mass.mass_window_size, self.moving_mass.mass_window_size, self.stop_loss, self.rsi.period, self.proft_take

   def __str__(self):
      return f"{self.moving_average.window_size}, {self.long_mass.mass_window_size}, {self.moving_mass.mass_window_size}, {self.stop_loss}, {self.rsi.period}, {self.proft_take}"
