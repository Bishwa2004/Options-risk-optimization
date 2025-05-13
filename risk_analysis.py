# 6. risk_analysis.py
import numpy as np

def expected_move(S, IV, T):
    return S * IV * np.sqrt(T / 252)

def breakeven_price(option_price, strike, option_type='call'):
    return strike + option_price if option_type == 'call' else strike - option_price

def max_loss(option_price):
    return option_price

def max_gain(S, strike, option_price, option_type='call'):
    if option_type == 'call':
        return max(0, S - strike) - option_price
    else:
        return max(0, strike - S) - option_price
