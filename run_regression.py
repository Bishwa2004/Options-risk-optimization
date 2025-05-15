import os
import pandas as pd
import statsmodels.api as sm
from analysis.utils import load_company_data

COMPANIES = ['AAPL']
DATA_DIR = 'data/'
OUTPUT_DIR = 'output/regression_results/'
os.makedirs(OUTPUT_DIR, exist_ok=True)

features = [
    'interest_rate', 'inflation', 'sentiment_score',
    'trading_volume', 'insider_sell_7d', 'institutional_net_buy',
    'implied_volatility_30d', 'call_put_vol_ratio'
]

def run_regression(ticker):
    filepath = os.path.join(DATA_DIR, f"{ticker}.xlsx")
    df = load_company_data(filepath)
    df = df.dropna(subset=features + ['stock_return'])

    X = df[features]
    y = df['stock_return']
    X = sm.add_constant(X)

    model = sm.OLS(y, X).fit()
    print(f"--- {ticker} ---")
    print(model.summary())

    with open(os.path.join(OUTPUT_DIR, f"{ticker}_regression.txt"), "w") as f:
        f.write(model.summary().as_text())

for ticker in COMPANIES:
    run_regression(ticker)
