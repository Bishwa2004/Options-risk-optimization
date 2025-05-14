# IMPORT MODULES
from data_fetch import fetch_stock_data, fetch_option_chain
from greeks import black_scholes_greeks
from signals import compute_signals
from backtest import simple_backtest
from valuation import get_valuation_metrics
from risk_analysis import expected_move, breakeven_price, max_loss, max_gain
from cluster_analysis import run_kmeans
from portfolio_manager import rank_trades

import matplotlib.pyplot as plt
import numpy as np

# SET PARAMETERS
ticker = "AAPL"
start_date = "2023-01-01"
end_date = "2023-12-31"
r = 0.05  # risk-free rate

# FETCH DATA
hist = fetch_stock_data(ticker, start_date, end_date)
option_chain = fetch_option_chain(ticker)
metrics = get_valuation_metrics(ticker)

# SIGNALS & BACKTEST
signals = compute_signals(hist)
portfolio = simple_backtest(signals)
portfolio.plot(title="Backtest Portfolio Value")
plt.show()

# DISPLAY VALUATION
print("Valuation Metrics:")
print(metrics)

# CHOOSE OPTION EXAMPLE
expiry = list(option_chain.keys())[0]
option = option_chain[expiry]["calls"].iloc[0]  # example: first call
S = hist['Close'].iloc[-1]
K = option['strike']
T = (pd.to_datetime(expiry) - pd.Timestamp.now()).days / 365
IV = option['impliedVolatility']
option_price = option['lastPrice']

# RISK & GREEKS
greeks = black_scholes_greeks(S, K, T, r, IV, option_type='call')
exp_move = expected_move(S, IV, T)
bep = breakeven_price(option_price, K, 'call')
loss = max_loss(option_price)
gain = max_gain(S, K, option_price, 'call')

print("\nGreeks:", greeks)
print("Expected Move:", round(exp_move, 2))
print("Breakeven Price:", round(bep, 2))
print("Max Loss:", round(loss, 2))
print("Max Gain (at current price):", round(gain, 2))

# CLUSTER EXAMPLE
df_cluster_input = hist[['Close']].copy()
df_cluster_input['volatility'] = hist['Close'].pct_change().rolling(10).std()
clustered = run_kmeans(df_cluster_input.dropna())
print("\nClustered Data Sample:")
print(clustered.tail())

# TRADE RANKING
trade_idea = {
    "ticker": ticker,
    "expected_gain": gain,
    "max_loss": loss,
    "option_price": option_price,
    "strike": K,
    "IV": IV
}
ranked_trades = rank_trades([trade_idea])
print("\nRanked Trade:")
print(ranked_trades)
