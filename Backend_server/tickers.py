import os
import pandas as pd

def tickers():
    try:
        # Get the path to the current file (tickers.py)
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # CSV is in the same directory (Backend_server)
        csv_path = os.path.join(base_dir, 'tickers_with_names.csv')

        # Read the CSV
        df = pd.read_csv(csv_path)
        tickers = df["Symbol"].tolist()
    except Exception as e:
        df = pd.DataFrame()
        tickers = []
        print("❌ Failed to load tickers:", e)

    return df, tickers
