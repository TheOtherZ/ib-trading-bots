import logging

from TraderCore.TradingCosts import TradingCosts, ibkr_trading_costs
from TraderCore.HelperFunctions import compute_percent_threshold
logger = logging.getLogger(__name__)

from ibapi.wrapper import BarData

from LiveCore.LiveTraderBase import LiveTraderBase
import LiveCore.LiveIndicator as ind

class TrendBot(LiveTraderBase):
   bar_list: list[BarData]
   velocity_list: list[float]

   def __init__(self, jump_threshold_percent: float, average_velocity_window: int, quick_velocity_window: int, stop_loss: float, profit_take: float, ticker: str, name: str = "UnnamedTrendTrader", capital: float = 10000, simulation: bool = True, trading_costs: TradingCosts = ibkr_trading_costs) -> None:
      super().__init__(name, capital, simulation, trading_costs)

      self.ticker = ticker

      self.stop_loss = stop_loss
      self.proft_take = profit_take
      
      self.jump_threshold_percent = jump_threshold_percent
      self.moving_average_velocity = ind.ValMovingAverage(average_velocity_window)
      self.quick_moving_average_velocity = ind.ValMovingAverage(quick_velocity_window)

      self.bar_list = []
      self.velocity_list = [0]
      self.data_length = average_velocity_window + 1

   def process(self, bar: BarData, new_bar=False):
      instant_velocity = bar.close - bar.open

      if new_bar:
         # Handle bar storage
         self.bar_list.append(bar)
         if len(self.bar_list) > self.data_length:
            self.bar_list.pop(0)
            if not self.trade_active and not self.simulation:
               logger.info(self.name + " Data fill complete, trading active for " + self.ticker)
            self.trade_active = True

         # Handle velocity storage
         self.velocity_list.append(instant_velocity)
         if len(self.velocity_list) > self.moving_average_velocity.window_size + 1:
            self.velocity_list.pop(0)
      else:
         self.bar_list[-1] = bar
         self.velocity_list[-1] = instant_velocity

      if len(self.velocity_list) > self.moving_average_velocity.window_size:
         self.moving_average_velocity.compute(self.velocity_list)
         self.quick_moving_average_velocity.compute(self.velocity_list)

      if not self.trade_active:
         return 0

      open_long = False
      open_short = False

      
      if self.num_held == 0:
         if open_long:
            self.order(bar.close, self.quantity_to_open)
         elif open_short:
            self.order(bar.close, -self.quantity_to_open)

      else:
         stop_short, stop_long = compute_percent_threshold(self.average_price, bar.close, self.stop_loss)
         profit_long, profit_short = compute_percent_threshold(self.average_price, bar.close, self.proft_take)


         close = False
         if self.num_held > 0 and (stop_long or profit_long):
            if stop_long:
               self.stop_trades += 1
            close = True
         elif self.num_held < 0 and (stop_short or profit_short):
            if stop_short:
               self.stop_trades += 1
            close = True
         
         if close:
            self.order(bar.close, -self.num_held)

      return super().process()
      
