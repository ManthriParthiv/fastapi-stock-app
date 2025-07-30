import os
import pandas as pd

def tickers():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Load fundamentals.csv
        fundamentals_path = os.path.join(base_dir, 'quantum_optimizer', 'data', 'fundamentals.csv')
        data = pd.read_csv(fundamentals_path)

        # Load tickers_with_names.csv
        tickers_csv_path = os.path.join(base_dir, 'tickers_with_names.csv')
        df = pd.read_csv(tickers_csv_path)

        csv_tickers = df["Symbol"].tolist()

        tickers = list(set(csv_tickers))

    except Exception as e:
        print("❌ Failed to load tickers:", e)
        data = pd.DataFrame()
        df = pd.DataFrame()
        tickers = []

    return data, df, tickers
