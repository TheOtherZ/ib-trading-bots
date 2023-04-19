#include "TradingCosts.h"
#include <algorithm>

TradingCosts::TradingCosts(double slipage, double commission_per_share, double sec_transaction, double finra_activity_fee, double min_fee) :
   _slipage(slipage),
   _commission(commission_per_share),
   _sec_transaction(sec_transaction),
   _finra_activity(finra_activity_fee),
   _min_fee(min_fee)
{
   return;
}

double TradingCosts::compute_cost(int quantity, double price, bool buy)
   {
      auto share_cost = std::max((_commission + _finra_activity) * quantity, _min_fee);
      auto total_slipage = _slipage * quantity;
      double sec_fee = 0.0;
      if (!buy)
      {
         sec_fee = (price * quantity + total_slipage) * _sec_transaction;
      }
      else
      {
         sec_fee = 0.0;
      }
      return share_cost + sec_fee, total_slipage;
   }