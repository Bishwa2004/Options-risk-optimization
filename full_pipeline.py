import os
import requests
import pandas as pd
import statsmodels.api as sm
from bs4 import BeautifulSoup
import yfinance as yf
from datetime import datetime, timedelta

# --- Configuration ---
ticker = "AAPL"
cik = "0000320193"
DATA_DIR = "data/"
OUTPUT_DIR = "output/regression_results/"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Fetch Form 4 Insider Trades ---
def fetch_form4_insider_trades(cik, limit=10):
    url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=4&owner=only&count={limit}&output=atom"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, "xml")
    entries = soup.find_all("entry")
    data = []
    for entry in entries:
        title = entry.title.text
        date = entry.updated.text
        link = entry.link['href']
        data.append({"title": title, "date": pd.to_datetime(date), "link": link})
    df = pd.DataFrame(data)
    df['shares_sold'] = df['title'].str.extract(r'(\d+(?:,\d+)*)', expand=False).str.replace(',', '').astype(float)
    df = df.groupby(df['date'].dt.date)['shares_sold'].sum().reset_index()
    df.columns = ['date', 'insider_sell_7d']
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df['insider_sell_7d'] = df['insider_sell_7d'].rolling(7).sum()
    return df

# --- Fetch Options Data from Yahoo Finance ---
def fetch_options_data_yf(ticker):
    t = yf.Ticker(ticker)
    expiry = t.options[0]
    chain = t.option_chain(expiry)
    call_vol = chain.calls['volume'].sum()
    put_vol = chain.puts['volume'].sum()
    call_put_vol_ratio = call_vol / put_vol if put_vol > 0 else 1
    iv = chain.calls['impliedVolatility'].mean()
    today = pd.to_datetime("today").normalize()
    return pd.DataFrame([{
        "date": today,
        "implied_volatility_30d": iv,
        "call_put_vol_ratio": call_put_vol_ratio
    }]).set_index("date")

# --- Generate Synthetic Macro + Return Data ---
def generate_macro_stock_data(start_date, days=60):
    dates = [start_date + timedelta(days=i) for i in range(days)]
    df = pd.DataFrame({
        "date": dates,
        "stock_return": [0.001 * ((i % 5) - 2) for i in range(days)],
        "interest_rate": [0.04 + 0.002 * (i % 3) for i in range(days)],
        "inflation": [0.02 + 0.001 * (i % 4) for i in range(days)],
        "sentiment_score": [0.7 + 0.05 * ((i % 4) - 2) for i in range(days)],
        "trading_volume": [1.1e7 + 5e5 * ((i % 6) - 3) for i in range(days)],
        "institutional_net_buy": [-100000 + 5000 * ((i % 5) - 2) for i in range(days)],
    })
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    return df

# --- Run Regression ---
def run_regression(df, ticker):
    features = [
        'interest_rate', 'inflation', 'sentiment_score',
        'trading_volume', 'insider_sell_7d', 'institutional_net_buy',
        'implied_volatility_30d', 'call_put_vol_ratio'
    ]
    df = df.dropna(subset=features + ['stock_return'])
    X = sm.add_constant(df[features])
    y = df['stock_return']
    model = sm.OLS(y, X).fit()
    result_path = os.path.join(OUTPUT_DIR, f"{ticker}_regression.txt")
    with open(result_path, "w") as f:
        f.write(model.summary().as_text())
    return model.summary().as_text()

# --- Combine & Execute ---
start_date = datetime.today() - timedelta(days=60)
df_macro = generate_macro_stock_data(start_date)
df_insider = fetch_form4_insider_trades(cik)
df_options = fetch_options_data_yf(ticker)

df = df_macro.join(df_insider, how='left').join(df_options, how='left')
df.to_excel(os.path.join(DATA_DIR, f"{ticker}.xlsx"))
regression_summary = run_regression(df, ticker)
print(regression_summary)
