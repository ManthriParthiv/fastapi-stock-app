import yfinance as yf
import pandas as pd
import time
from .logger import api_logger


def fetch_and_cache(tickers, outpath, period="6mo",auto_adjust=True):
    """
    1) Download last `period` of data for tickers
    2) Log duration
    3) Keep only Close (or Adj Close)
    4) Write CSV to outpath
    """
    start = time.time()
    df = yf.download(tickers, period=period)
    elapsed = time.time() - start
    api_logger.log_call("yfinance.download", elapsed)

    # reduce to Close series
    if "Close" in df.columns:
        df = df["Close"]
    else:
        df = df["Adj Close"]

    df.to_csv(outpath)
    return df


if __name__ == "__main__":
    tickers = ["TCS.NS", "SIEMENS.NS", "NHPC.NS", "IDEA.NS"]
    df = fetch_and_cache(tickers, "./data/last6m.csv")
    print("API call stats:", api_logger.summary())