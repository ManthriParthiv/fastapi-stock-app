import pandas as pd

def tickers():
    try:
        df = pd.read_csv("tickers_with_names.csv")  # CSV must have 'Symbol' and 'Name'
        tickers = df["Symbol"].tolist()
    except Exception as e:
        df = pd.DataFrame()
        tickers = []
        print("❌ Failed to load tickers:", e)
    return df, tickers