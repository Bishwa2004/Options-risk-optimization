# 5. valuation.py
import yfinance as yf

def get_valuation_metrics(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    metrics = {
        'pe_ratio': info.get('trailingPE'),
        'peg_ratio': info.get('pegRatio'),
        'ev_to_ebitda': info.get('enterpriseToEbitda'),
        'roe': info.get('returnOnEquity'),
        'revenue_growth': info.get('revenueGrowth'),
    }
    return metrics
