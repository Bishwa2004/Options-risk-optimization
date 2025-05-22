# options_flow_visualizer.py

import os
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load API key from .env if needed for OpenAI or HuggingFace
load_dotenv()

# Replace with actual OpenAI or HuggingFace call later
import requests

def analyze_sentiment_with_llm(prompt):
    HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY")
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt}

    response = requests.post(
        "https://api-inference.huggingface.co/models/google/gemma-7b-it",
        headers=headers,
        json=payload
    )
    return {"summary": response.json()[0]['generated_text'], "sentiment": "Bullish"}  # Simplify for now

#def analyze_sentiment_with_llm(prompt):
    # Stub - replace with actual API call
    #return {
        #"summary": "Traders are positioning for downside on AAPL with high put volume at 170 strike.",
        #"sentiment": "Bearish"
   # }
try:
    response = requests.post(...)
    output = response.json()
    if isinstance(output, list):
        summary = output[0].get('generated_text', '')
    else:
        summary = output.get('generated_text', '')
except Exception as e:
    summary = "Error in LLM call: " + str(e)
if "bearish" in summary.lower():
    sentiment = "Bearish"
elif "bullish" in summary.lower():
    sentiment = "Bullish"
else:
    sentiment = "Neutral"

def fetch_options_flow(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    expiry = ticker.options[0]  # Nearest expiry
    chain = ticker.option_chain(expiry)

    # Compute basic metrics
    call_vol = chain.calls['volume'].sum()
    put_vol = chain.puts['volume'].sum()
    iv_calls = chain.calls['impliedVolatility'].mean()
    iv_puts = chain.puts['impliedVolatility'].mean()
    vol_ratio = call_vol / put_vol if put_vol > 0 else None
    iv_skew = iv_calls - iv_puts

    flow_summary = {
        "call_vol": int(call_vol),
        "put_vol": int(put_vol),
        "vol_ratio": round(vol_ratio, 2) if vol_ratio else "N/A",
        "iv_calls": round(iv_calls, 4),
        "iv_puts": round(iv_puts, 4),
        "iv_skew": round(iv_skew, 4),
        "expiry": expiry
    }
    return flow_summary

def build_prompt(flow_summary, ticker):
    prompt = f"""
Options sentiment analysis for {ticker}:
- Call volume: {flow_summary['call_vol']}
- Put volume: {flow_summary['put_vol']}
- Call/Put volume ratio: {flow_summary['vol_ratio']}
- Implied Volatility Skew (Calls - Puts): {flow_summary['iv_skew']}
- Expiry date: {flow_summary['expiry']}

What does this imply about market sentiment and positioning?
"""
    return prompt

def generate_lovable_payload(flow_summary, analysis_result):
    return {
        "cards": [
            {
                "type": "summary",
                "title": "Options Flow Analysis",
                "content": analysis_result["summary"]
            },
            {
                "type": "metric",
                "title": "Sentiment",
                "value": analysis_result["sentiment"],
                "color": "green" if analysis_result["sentiment"] == "Bullish" else "red"
            },
            {
                "type": "table",
                "title": "Options Flow Summary",
                "columns": ["Metric", "Value"],
                "rows": [
                    ["Call Volume", flow_summary["call_vol"]],
                    ["Put Volume", flow_summary["put_vol"]],
                    ["Call/Put Ratio", flow_summary["vol_ratio"]],
                    ["IV (Calls)", flow_summary["iv_calls"]],
                    ["IV (Puts)", flow_summary["iv_puts"]],
                    ["IV Skew", flow_summary["iv_skew"]]
                ]
            }
        ]
    }

if __name__ == "__main__":
    ticker = "AAPL"
    flow_summary = fetch_options_flow(ticker)
    prompt = build_prompt(flow_summary, ticker)
    analysis_result = analyze_sentiment_with_llm(prompt)
    payload = generate_lovable_payload(flow_summary, analysis_result)

    # Output to JSON or API call to Lovable frontend
    import json
    with open("lovable_output.json", "w") as f:
        json.dump(payload, f, indent=2)

    print("✅ Sentiment analysis complete. Check lovable_output.json")
