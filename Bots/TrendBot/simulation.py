from LiveCore.Simulator import simulate_ticker_group, simulate_bot_pool, forward_test

from TrendBot import TrendBot

def build_config_list(frame="fast") -> list:
   config_list = []

   # average_window, crossing_window, crossing_threshold, stop_loss, rsi_window, profit_horizon, profit_take
   if frame == "fast":
      average_window_list = [280, 120]
      crossing_window_long_list = [40, 60, 80]
      crossing_window_list = [10, 16, 24]
      stop_loss_list = [2.0]
      rsi_list = [8]
      profit_take_list = [3.0, 4.0, 5.0]