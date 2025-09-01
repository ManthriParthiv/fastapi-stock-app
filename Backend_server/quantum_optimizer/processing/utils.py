import numpy as np
import pandas as pd
from typing import Tuple

def load_returns(path_csv: str) -> pd.DataFrame:
    """
    Read a CSV of prices (indexed by date), compute daily %
    returns, drop NaNs, and return.
    """
    df = pd.read_csv(path_csv, index_col=0, parse_dates=True)
    returns = df.pct_change().dropna()
    return returns


def annualize(returns: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    """
    From daily returns DataFrame:
      - mean vector μ (annualized)
      - covariance matrix Σ (annualized)
    """
    # Check if returns is a DataFrame with proper structure
    if isinstance(returns, pd.DataFrame):
        mean = returns.mean() * 252
        cov = returns.cov() * 252
        return mean.values.astype(np.float64), cov.values.astype(np.float64)
    else:
        # Handle case where returns might be a Series or array
        mean = np.mean(returns) * 252 if hasattr(returns, '__iter__') else returns * 252
        # For covariance, we need at least 2D data
        if hasattr(returns, 'shape') and len(returns.shape) > 1:
            cov = np.cov(returns, rowvar=False) * 252
        else:
            # If single asset, return variance as 1x1 matrix
            cov = np.array([[np.var(returns) * 252]]).astype(np.float64)
        return np.array(mean).astype(np.float64), cov.astype(np.float64)


def load_features(returns_csv, fund_csv):
    import pandas as pd

    # loads a date×ticker return table, stacks to rows, then merges fundamentals
    r = pd.read_csv(returns_csv, index_col=0, parse_dates=True)
    f = pd.read_csv(fund_csv, index_col=0)
    stacked = r.stack().rename("Return").reset_index()
    stacked.columns = ["Date", "Ticker", "Return"]
    features = stacked.join(f, on="Ticker")
    return features


def validate_fundamentals(fundamentals: dict, tickers: list) -> dict:
    """
    Ensure all required parameters are present with fallback values
    """
    DEFAULT_VALUES = {
        'PE': 15.0, 'PB': 3.0, 'ROE': 0.15, 'EV/EBITDA': 12.0,
        'RevenueGrowth': 0.05, 'PEGRatio': 1.0, 'NetMargin': 0.1,
        'FreeCF': 0.0, 'OpMargin': 0.15, 'P/S': 2.0, 'Payout': 0.3,
        'CurrRatio': 1.5
    }
    
    validated = {}
    for t in tickers:
        validated[t] = {}
        for param in DEFAULT_VALUES:
            val = fundamentals.get(t, {}).get(param)
            validated[t][param] = DEFAULT_VALUES[param] if val is None or np.isnan(val) else float(val)
    return validated