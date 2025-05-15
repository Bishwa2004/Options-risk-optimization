import pandas as pd

def load_company_data(filepath):
    df = pd.read_excel(filepath)
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    return df

def merge_external_data(stock_df, external_df, on='date'):
    external_df['date'] = pd.to_datetime(external_df['date'])
    external_df = external_df.set_index('date')
    return stock_df.merge(external_df, how='left', left_index=True, right_index=True)
