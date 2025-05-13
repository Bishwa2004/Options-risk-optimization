# 8. portfolio_manager.py
import pandas as pd

def rank_trades(trade_data):
    df = pd.DataFrame(trade_data)
    df['risk_reward'] = df['expected_gain'] / df['max_loss']
    df_sorted = df.sort_values(by='risk_reward', ascending=False)
    return df_sorted
