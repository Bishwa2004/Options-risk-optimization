 3. signals.py
def compute_signals(stock_df):
    signals = pd.DataFrame(index=stock_df.index)
    signals['price'] = stock_df['Close']
    signals['sma20'] = stock_df['Close'].rolling(window=20).mean()
    signals['sma50'] = stock_df['Close'].rolling(window=50).mean()
    signals['signal'] = 0
    signals['signal'][signals['sma20'] > signals['sma50']] = 1
    signals['signal'][signals['sma20'] < signals['sma50']] = -1
    return signals
