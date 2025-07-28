from pathlib import Path
import pandas as pd

def load_cached_data():
    """Safely loads your existing cache without modifications"""
    data_path = Path(__file__).parent.parent/"quantum_optimizer"/"data"
    return {
        "prices": pd.read_csv(data_path/"last6m.csv", index_col=0, parse_dates=True),
        "fundamentals": pd.read_csv(data_path/"fundamentals.csv", index_col=0)
    }

VALID_TICKERS = {"TCS.NS", "SIEMENS.NS", "NHPC.NS", "IDEA.NS"}