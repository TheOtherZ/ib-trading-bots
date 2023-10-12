import logging
logger = logging.getLogger(__name__)

from ibapi.wrapper import BarData

from LiveCore.LiveTraderBase import LiveTraderBase
from TraderCore.TradingCosts import ibkr_trading_costs, TradingCosts
import LiveCore.LiveIndicator as ind
from TraderCore.Indicators import RSIOscillator, MovingMass
from TraderCore.HelperFunctions import compute_percent_threshold


class MeanRegressionBotLive(LiveTraderBase):
   def __init__(self, average_window: int, momentum_window_long: int, momentum_window: int, stop_loss: float, rsi_window: int, profit_take: float, ticker: str, capital: float=10000.0, cost: TradingCosts=ibkr_trading_costs, simulation: bool = True, name: str = "none_bot") -> None:
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
      self.moving_mass_history = []

      self.bar_list = []
      self.data_length = average_window + momentum_window_long + 5 #Some padding
      self.trade_active = False
      self.quantity_to_open = 1
      self.history_length = self.data_length * 2

      self.stop_loss = stop_loss
      self.proft_take = profit_take

      self.purge_count = 8
      self.bars_to_purge = self.retrieve_value("bars_to_purge", 0)
      
      self.last_bar = BarData()
      self.live = False
   
   def process(self, bar: BarData, new_bar=False):
      if new_bar:
         # if self.trading_enabled and not self.simulation:
         #    print(self.order_msg())
         self.bar_list.append(bar)
         if len(self.bar_list) > self.history_length:
            self.bar_list.pop(0)
            if not self.trade_active and not self.simulation:
               logger.info(self.name + " Data fill complete, trading active for " + self.ticker)
            self.trade_active = True
         self.rsi.compute(self.last_bar)
      else:
         self.bar_list[-1] = bar

      self.moving_average.compute(self.bar_list)
      if self.live:
         self.new_rsi.live = True
      self.new_rsi.compute(bar, new_bar)

      self.quantity_to_open = self.compute_share_quantity(bar.close, self.capital)

      if len(self.bar_list) > self.moving_average.window_size:
         if new_bar:
            self.long_mass.compute(self.moving_average.value, self.last_bar)
            self.moving_mass.compute(self.moving_average.value, self.last_bar)
         self.new_long_mass.compute(self.moving_average.value, bar, new_bar)
         self.new_moving_mass.compute(self.moving_average.value, bar, new_bar)
         if new_bar:
            self.moving_mass_history.append(self.new_long_mass.value)
            if len(self.moving_mass_history) > self.data_length:
               self.moving_mass_history.pop(0)

      # if self.trading_enabled and not self.simulation:
      #    # pass # TODO
      #    print(f"{self.ticker}: CLOSE: {round(bar.close, 5)}, BARAVG: {round(bar.wap, 5)}, AVG: {round(self.moving_average.value, 3)}, RSI: {round(self.rsi.value, 2)} {round(self.new_rsi.value, 2)}, LONG: {round(self.long_mass.value, 8)} {round(self.new_long_mass.value, 8)}, SHORT: {round(self.moving_mass.value, 2)} {round(self.new_moving_mass.value, 2)}") #TODO
      
      if self.bars_to_purge > 0 and new_bar:
         self.bars_to_purge -= 1
         self.save_value("bars_to_purge", self.bars_to_purge)

      self.last_bar = bar
      if not self.trade_active or self.bars_to_purge != 0:
         return 0
      #TODO
      long_mass_upper = max(self.moving_mass_history) #TODO: is this fudge factor good?
      long_mass_lower = min(self.moving_mass_history) #TODO: is this fudge factor good?

      absolute_lower = 50
      absolute_upper = 50
      short_term_low = long_mass_lower - 10 if long_mass_lower - 10 < absolute_lower else absolute_lower
      short_term_high = long_mass_upper + 10 if long_mass_upper + 10 > absolute_upper else absolute_upper
      long_term_low = long_mass_lower + 10 if long_mass_lower + 10 < absolute_lower else absolute_lower
      long_term_high = long_mass_upper - 10 if long_mass_upper - 10 > absolute_upper else absolute_upper
      open_long = self.new_moving_mass.value < short_term_low  and self.new_long_mass.value > long_term_high
      open_short = self.new_moving_mass.value > short_term_high and self.new_long_mass.value < long_term_low

      
      if self.num_held == 0:
         if open_long:
            self.order(bar.close, self.quantity_to_open)
         elif open_short:
            self.order(bar.close, -self.quantity_to_open)

      else:
         stop_short, stop_long = compute_percent_threshold(self.average_price, bar.close, self.stop_loss)
         profit_long, profit_short = compute_percent_threshold(self.average_price, bar.close, self.proft_take)


         close = False
         if self.num_held > 0 and (stop_long or self.moving_mass.value > 85 or profit_long):
            if stop_long:
               self.stop_trades += 1
               self.bars_to_purge = self.purge_count
               self.save_value("bars_to_purge", self.bars_to_purge)
            close = True
         elif self.num_held < 0 and (stop_short or self.moving_mass.value < 15 or profit_short):
            if stop_short:
               self.stop_trades += 1
               self.bars_to_purge = self.purge_count
               self.save_value("bars_to_purge", self.bars_to_purge)
            close = True
         
         if close:
            if not (stop_long or stop_short):
               self.bars_to_purge = 1
               self.save_value("bars_to_purge", self.bars_to_purge)
            self.order(bar.close, -self.num_held)

      return super().process()
   
   def confirm_order(self, price: float, quantity: int):
      return super().confirm_order(price, quantity)

   def get_parameters(self):
      return self.moving_average.window_size, self.long_mass.mass_window_size, self.moving_mass.mass_window_size, self.stop_loss, self.rsi.period, self.proft_take
   
   def order_msg(self) -> str:
      return super().order_msg() + f"- RSI: {self.new_rsi.value}, AVG: {round(self.moving_average.value, 3)}, RSI: {round(self.new_rsi.value, 3)}, LONG: {round(self.new_long_mass.value, 3)}, SHORT: {round(self.new_moving_mass.value, 3)}"

   def __str__(self):
      return f"{self.moving_average.window_size}, {self.long_mass.mass_window_size}, {self.moving_mass.mass_window_size}, {self.stop_loss}, {self.rsi.period}, {self.proft_take}"
