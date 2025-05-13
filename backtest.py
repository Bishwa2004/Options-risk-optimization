# 4. backtest.py
def simple_backtest(signals, initial_capital=10000):
    positions = signals['signal'].shift(1).fillna(0)
    returns = signals['price'].pct_change().fillna(0)
    strategy_returns = positions * returns
    portfolio = (1 + strategy_returns).cumprod() * initial_capital
    return portfolio
