class TradingCosts
{
public:
    TradingCosts(double slipage, double commission_per_share, double sec_transaction, double finra_activity_fee, double min_fee);
    ~TradingCosts() = default;

    double compute_cost(int quantity, double price, bool buy);
private:
    double _slipage;
    double _commission;
    double _sec_transaction;
    double _finra_activity;
    double _min_fee;
};

// ibkr_trading_costs = TradingCosts(0.02, 0.005, 0.0000229, 0.00013, 1.00)