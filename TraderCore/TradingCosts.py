class TradingCosts(object):
   def __init__(self, slipage, commission_per_share, sec_transaction, finra_activity_fee, min_fee):
      self.slipage = slipage
      self.commission = commission_per_share
      self.sec_transaction = sec_transaction
      self.finra_activity = finra_activity_fee
      self.min_fee = min_fee

   def compute_cost(self, quantity, price, buy):
      share_cost = max((self.commission + self.finra_activity) * quantity, self.min_fee)
      total_slipage = self.slipage * quantity
      if not buy:
         sec_fee = (price * quantity + total_slipage) * self.sec_transaction
      else:
         sec_fee = 0.0
      return share_cost + sec_fee, total_slipage

   def __str__(self) -> str:
      return f"Costs: {self.slipage}, {self.commission}, {self.sec_transaction}, {self.finra_activity}, {self.min_fee}"

ibkr_trading_costs = TradingCosts(0.02, 0.005, 0.0000229, 0.00013, 1.00)