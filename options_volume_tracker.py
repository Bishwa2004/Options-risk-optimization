# options_volume_tracker.py
# Track S&P 500 options volume for selected expiry and strike range, detect anomalies, visualize, LLM summary, and trade recommendation

import yfinance as yf
import pandas as pd
import json
from datetime import datetime
from scipy.stats import zscore
import os
import matplotlib.pyplot as plt
import openai
from dotenv import load_dotenv

# --- Config ---
EXPIRY_INDEX = 0
STRIKE_RANGE = (170, 180)
MAX_TICKERS = 50
HISTORY_DIR = "sp500_volume_history"
os.makedirs(HISTORY_DIR, exist_ok=True)
load_dotenv()

# Get S&P 500 tickers
sp500 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
tickers = sp500['Symbol'].tolist()

# Ticker Watchlist (custom user-defined for priority scan)
WATCHLIST = ["AAPL", "TSLA", "NVDA", "MSFT", "META"]

# Today's date
today = datetime.today().strftime("%Y-%m-%d")
today_results = []

# Loop through tickers
for symbol in tickers[:MAX_TICKERS]:
    try:
        t = yf.Ticker(symbol)
        expirations = t.options
        if not expirations:
            continue
        expiry = expirations[EXPIRY_INDEX]
        chain = t.option_chain(expiry)
        calls = chain.calls
        puts = chain.puts
        call_filter = calls[(calls['strike'] >= STRIKE_RANGE[0]) & (calls['strike'] <= STRIKE_RANGE[1])]
        put_filter = puts[(puts['strike'] >= STRIKE_RANGE[0]) & (puts['strike'] <= STRIKE_RANGE[1])]
        call_vol = call_filter['volume'].sum()
        put_vol = put_filter['volume'].sum()
        total_vol = call_vol + put_vol
        call_iv = call_filter['impliedVolatility'].mean()
        put_iv = put_filter['impliedVolatility'].mean()

        today_results.append({
            "ticker": symbol,
            "expiry": expiry,
            "strike_range": f"{STRIKE_RANGE[0]}-{STRIKE_RANGE[1]}",
            "call_volume": int(call_vol),
            "put_volume": int(put_vol),
            "total_volume": int(total_vol),
            "call_iv": round(call_iv, 4) if not pd.isna(call_iv) else None,
            "put_iv": round(put_iv, 4) if not pd.isna(put_iv) else None
        })

    except Exception as e:
        print(f"{symbol}: failed ({str(e)})")

# Save today's data
filename_today = f"{HISTORY_DIR}/sp500_options_volume_{today}.json"
with open(filename_today, "w") as f:
    json.dump(today_results, f, indent=2)
print(f"✅ Volume tracking complete. Saved to {filename_today}")

# Anomaly detection
history_file = f"{HISTORY_DIR}/volume_history.csv"
try:
    df_hist = pd.read_csv(history_file)
except FileNotFoundError:
    df_hist = pd.DataFrame(columns=["date", "ticker", "total_volume"])

df_today = pd.DataFrame(today_results)[["ticker", "total_volume"]]
df_today["date"] = today
df_combined = pd.concat([df_hist, df_today], ignore_index=True)
df_combined = df_combined.sort_values(by=["ticker", "date"])
df_combined = df_combined.groupby("ticker").tail(30)
df_combined.to_csv(history_file, index=False)

df_anomalies = df_combined.groupby("ticker")["total_volume"].apply(zscore).reset_index()
df_anomalies = df_anomalies.rename(columns={"total_volume": "z_score"})
df_final = df_combined.merge(df_anomalies, on=["ticker", "date"])
df_final_today = df_final[df_final["date"] == today]
anomalies_detected = df_final_today[df_final_today["z_score"].abs() >= 2.5]
anomaly_output_file = f"{HISTORY_DIR}/anomalies_{today}.json"
anomalies_detected.to_json(anomaly_output_file, orient="records", indent=2)

print(f"🚨 Anomaly detection complete. {len(anomalies_detected)} tickers flagged.\nSaved to {anomaly_output_file}")

# Visualization
plt.figure(figsize=(10, 6))
plot_df = df_final_today.sort_values(by="z_score", ascending=False).head(15)
plt.barh(plot_df['ticker'], plot_df['z_score'], color='red')
plt.xlabel("Z-Score")
plt.title(f"Top Options Volume Anomalies – {today}")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f"{HISTORY_DIR}/anomalies_plot_{today}.png")
print(f"📊 Saved anomaly plot to anomalies_plot_{today}.png")

# LLM Summary and Trade Idea
if "OPENAI_API_KEY" in os.environ:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    llm_summaries = []
    for row in anomalies_detected.to_dict(orient="records"):
        prompt = f"""
The options volume for {row['ticker']} rose by {round(row['z_score'], 2)} standard deviations today.
Strike range: {STRIKE_RANGE[0]}–{STRIKE_RANGE[1]}, Expiry: {today}.
Call IV: {row['call_iv']:.2%}, Put IV: {row['put_iv']:.2%}.

1. Explain the sentiment or possible cause.
2. Suggest a potential options trade a trader might consider.
3. Include reasoning for the trade idea.
"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            summary = response.choices[0].message['content']
            row['llm_summary'] = summary
            llm_summaries.append(row)
        except Exception as e:
            print(f"LLM failed for {row['ticker']}: {str(e)}")

    llm_file = f"{HISTORY_DIR}/llm_anomalies_{today}.json"
    with open(llm_file, "w") as f:
        json.dump(llm_summaries, f, indent=2)
    print(f"🧠 LLM summaries saved to {llm_file}")

# Save a simplified JSON for graphing directly (charting in Lovable)
chart_data = plot_df[['ticker', 'z_score']].to_dict(orient="records")
with open(f"{HISTORY_DIR}/graph_data_{today}.json", "w") as f:
    json.dump(chart_data, f, indent=2)
print("📊 Saved chart-ready JSON for Lovable")
