import numpy as np
import pandas as pd


def load_returns(path_csv: str) -> pd.DataFrame:
    """
    Read a CSV of prices (indexed by date), compute daily %
    returns, drop NaNs, and return.
    """
    df = pd.read_csv(path_csv, index_col=0, parse_dates=True)
    returns = df.pct_change().dropna()
    return returns


def annualize(returns: pd.DataFrame):
    """
    From daily returns DataFrame:
      - mean vector μ (annualized)
      - covariance matrix Σ (annualized)
    """
    mean = returns.mean() * 252
    cov = returns.cov() * 252
    return mean.values, cov.values


def load_features(returns_csv, fund_csv):
    import pandas as pd

    # loads a date×ticker return table, stacks to rows, then merges fundamentals
    r = pd.read_csv(returns_csv, index_col=0, parse_dates=True)
    f = pd.read_csv(fund_csv, index_col=0)
    stacked = r.stack().rename("Return").reset_index()
    stacked.columns = ["Date", "Ticker", "Return"]
    features = stacked.join(f, on="Ticker")
    return features
