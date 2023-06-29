import LiveCore.LiveTraderBase as ltb
import unittest as ut

class TestLiveTraderBase(ut.TestCase):
   def test_open_close_long_profit_no_sim(self):
      trader_under_test = ltb.LiveTraderBase(simulation=False)
      trader_under_test.trading_enabled = True
      # Open long position
      open_price = 45.50
      num_shares = 100
      trader_under_test.order(open_price, num_shares)
      self.assertEqual(trader_under_test.num_held, 0)
      self.assertEqual(trader_under_test.num_pending, num_shares)
      self.assertEqual(trader_under_test.average_price, open_price)
      self.assertEqual(trader_under_test.process(), num_shares)

      # Confirm position open
      actual_open_price = 45.51
      trader_under_test.confirm_order(actual_open_price, num_shares)
      self.assertEqual(trader_under_test.num_held, num_shares)
      self.assertEqual(trader_under_test.num_pending, 0)
      self.assertEqual(trader_under_test.average_price, actual_open_price)
      self.assertEqual(trader_under_test.process(), 0)

      # Close long position
      close_price = 60.0
      trader_under_test.order(close_price, -num_shares)
      self.assertEqual(trader_under_test.num_held, num_shares)
      self.assertEqual(trader_under_test.num_pending, -num_shares)
      self.assertEqual(trader_under_test.average_price, actual_open_price)
      self.assertEqual(trader_under_test.process(), -num_shares)

      # Confirm close
      actual_close_price = 59.98
      trader_under_test.confirm_order(actual_close_price, -num_shares)
      self.assertEqual(trader_under_test.num_held, 0)
      self.assertEqual(trader_under_test.num_pending, 0)
      self.assertEqual(trader_under_test.average_price, 0)
      self.assertEqual(trader_under_test.process(), 0)

      # Check stats
      stats = trader_under_test.get_stats()
      self.assertEqual(stats[0], (actual_close_price - actual_open_price) * num_shares) # should make profit
      self.assertEqual(stats[1], 0) # drawdown
      self.assertEqual(stats[2], 1) # win_percent
      self.assertEqual(stats[3], 1) # num_trades
      self.assertEqual(stats[4], 1) # long_trades
      self.assertEqual(stats[5], 0) # short_trades
      self.assertEqual(stats[6], 0) # stop_trades

   def test_open_close_short_profit_no_sim(self):
         trader_under_test = ltb.LiveTraderBase(simulation=False)
         trader_under_test.trading_enabled = True
         # Open long position
         open_price = 45.50
         num_shares = 100
         trader_under_test.order(open_price, -num_shares)
         self.assertEqual(trader_under_test.num_held, 0)
         self.assertEqual(trader_under_test.num_pending, -num_shares)
         self.assertEqual(trader_under_test.average_price, open_price)
         self.assertEqual(trader_under_test.process(), -num_shares)

         # Confirm position open
         actual_open_price = 45.49
         trader_under_test.confirm_order(actual_open_price, -num_shares)
         self.assertEqual(trader_under_test.num_held, -num_shares)
         self.assertEqual(trader_under_test.num_pending, 0)
         self.assertEqual(trader_under_test.average_price, actual_open_price)
         self.assertEqual(trader_under_test.process(), 0)

         # Close long position
         close_price = 30.0
         trader_under_test.order(close_price, num_shares)
         self.assertEqual(trader_under_test.num_held, -num_shares)
         self.assertEqual(trader_under_test.num_pending, num_shares)
         self.assertEqual(trader_under_test.average_price, actual_open_price)
         self.assertEqual(trader_under_test.process(), num_shares)

         # Confirm close
         actual_close_price = 30.01
         trader_under_test.confirm_order(actual_close_price, num_shares)
         self.assertEqual(trader_under_test.num_held, 0)
         self.assertEqual(trader_under_test.num_pending, 0)
         self.assertEqual(trader_under_test.average_price, 0)
         self.assertEqual(trader_under_test.process(), 0)

         # Check stats
         stats = trader_under_test.get_stats()
         self.assertEqual(stats[0], (actual_open_price - actual_close_price) * num_shares) # should make profit
         self.assertEqual(stats[1], 0) # drawdown
         self.assertEqual(stats[2], 1) # win_percent
         self.assertEqual(stats[3], 1) # num_trades
         self.assertEqual(stats[4], 0) # long_trades
         self.assertEqual(stats[5], 1) # short_trades
         self.assertEqual(stats[6], 0) # stop_trades


   def test_open_close_long_profit_with_sim(self):
      trader_under_test = ltb.LiveTraderBase(simulation=True)
      # Open long position
      open_price = 45.50
      num_shares = 100
      trader_under_test.order(open_price, num_shares)
      self.assertEqual(trader_under_test.num_held, num_shares)
      self.assertEqual(trader_under_test.num_pending, 0)
      self.assertEqual(trader_under_test.average_price, open_price)
      self.assertEqual(trader_under_test.process(), 0)

      # Close long position
      close_price = 60.0
      trader_under_test.order(close_price, -num_shares)
      self.assertEqual(trader_under_test.num_held, 0)
      self.assertEqual(trader_under_test.num_pending, 0)
      self.assertEqual(trader_under_test.average_price, 0)
      self.assertEqual(trader_under_test.process(), 0)


      # Check stats
      stats = trader_under_test.get_stats()
      self.assertGreater(stats[0], 0) # should make profit
      self.assertLess(stats[1], 0) # drawdown slightly degative for simulated costs
      self.assertEqual(stats[2], 1) # win_percent
      self.assertEqual(stats[3], 1) # num_trades
      self.assertEqual(stats[4], 1) # long_trades
      self.assertEqual(stats[5], 0) # short_trades
      self.assertEqual(stats[6], 0) # stop_trades

   def test_open_close_short_profit_with_sim(self):
      trader_under_test = ltb.LiveTraderBase(simulation=True)
      # Open long position
      open_price = 45.50
      num_shares = 100
      trader_under_test.order(open_price, -num_shares)
      self.assertEqual(trader_under_test.num_held, -num_shares)
      self.assertEqual(trader_under_test.num_pending, 0)
      self.assertEqual(trader_under_test.average_price, open_price)
      self.assertEqual(trader_under_test.process(), 0)

      # Close long position
      close_price = 30.0
      trader_under_test.order(close_price, num_shares)
      self.assertEqual(trader_under_test.num_held, 0)
      self.assertEqual(trader_under_test.num_pending, 0)
      self.assertEqual(trader_under_test.average_price, 0)
      self.assertEqual(trader_under_test.process(), 0)

      # Check stats
      stats = trader_under_test.get_stats()
      self.assertGreater(stats[0], 0) # should make profit
      self.assertLess(stats[1], 0) # drawdown slightly degative for simulated costs
      self.assertEqual(stats[2], 1) # win_percent
      self.assertEqual(stats[3], 1) # num_trades
      self.assertEqual(stats[4], 0) # long_trades
      self.assertEqual(stats[5], 1) # short_trades
      self.assertEqual(stats[6], 0) # stop_trades
