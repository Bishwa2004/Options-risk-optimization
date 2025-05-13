# 1. data_fetch.py
import yfinance as yf
import pandas as pd

def fetch_stock_data(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
    hist = stock.history(start=start_date, end=end_date)
    return hist

def fetch_option_chain(ticker):
    stock = yf.Ticker(ticker)
    expirations = stock.options
    chains = {}
    for expiry in expirations[:2]:  # limit for speed
        calls = stock.option_chain(expiry).calls
        puts = stock.option_chain(expiry).puts
        chains[expiry] = {"calls": calls, "puts": puts}
    return chains
