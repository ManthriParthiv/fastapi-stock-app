import os
import time
import pandas as pd
import numpy as np
from typing import List, Dict  # Add this import at the top

from preprocessing.fetch_data import fetch_and_cache   
from processing.utils import load_returns, load_features, annualize
from processing.vqe_portfolio import run_vqe
from postprocessing.analyze import compile_results
from postprocessing.visualize import plot_weights

def load_fundamentals_as_dict(tickers: List[str], csv_path: str) -> Dict[str, Dict[str, float]]:
    """Load fundamentals as dictionary format expected by VQE"""
    df = pd.read_csv(csv_path, index_col=0)
    return {
        t: {
            "PE": float(df.at[t, "PE"]),
            "PB": float(df.at[t, "PB"]),
            "ROE": float(df.at[t, "ROE"])
        }
        for t in tickers
    }

if __name__ == "__main__":
    TICKERS = ["TCS.NS", "SIEMENS.NS", "NHPC.NS", "IDEA.NS"]
    CSV_PATH = "data/last6m.csv"
    FUND_CSV = "data/fundamentals.csv"

    t0 = time.time()
    
    # ── Prices ────────────────────────────────────────────────
    if os.path.exists(CSV_PATH):
        print(f"⏩ Loading cached prices from {CSV_PATH}")
        df = pd.read_csv(CSV_PATH, index_col=0, parse_dates=True)
    else:
        print("⏳ Cache miss – fetching prices …")
        from preprocessing.parallel_fetch import parallel_fetch
        groups = [[t] for t in TICKERS]
        outpaths = [f"data/{t}.csv" for t in TICKERS]
        fetched = parallel_fetch(groups, outpaths, period="6mo", max_workers=4)
        df = pd.concat(fetched.values(), axis=1)
        df.to_csv(CSV_PATH)
    print("Prices shape:", df.shape)

    # ── Fundamentals ─────────────────────────────────────────
    if os.path.exists(FUND_CSV):
        print(f"⏩ Loading cached fundamentals from {FUND_CSV}")
        fundamentals = load_fundamentals_as_dict(TICKERS, FUND_CSV)
    else:
        print("⏳ Cache miss – fetching fundamentals …")
        from preprocessing.fetch_fundamentals import fetch_fundamentals
        fetch_fundamentals(TICKERS, FUND_CSV)
        fundamentals = load_fundamentals_as_dict(TICKERS, FUND_CSV)

    # build your features & stats
    features = load_features(CSV_PATH, FUND_CSV)
    mu, cov = annualize(load_returns(CSV_PATH))
    t1 = time.time()
# Add this right before VQE call:
    print("\nData Validation:")
    print(f"mu: {mu.shape}, type: {mu.dtype}")
    print(f"cov: {cov.shape}, type: {cov.dtype}")
    print("Fundamentals PE values:", [fundamentals[t].get('PE', 'MISSING') for t in sorted(fundamentals)])

# Clean NaN values in fundamentals
    clean_fundamentals = {
        t: {
        'PE': 1.0 if np.isnan(fundamentals[t].get('PE', np.nan)) else float(fundamentals[t]['PE']),
        'PB': 1.0 if np.isnan(fundamentals[t].get('PB', np.nan)) else float(fundamentals[t]['PB']),
        'ROE': 0.1 if np.isnan(fundamentals[t].get('ROE', np.nan)) else float(fundamentals[t]['ROE'])
      }
        for t in fundamentals
}

# Run VQE with cleaned data
    weights, vqe_res = run_vqe(
       mu=mu.astype(np.float64),
       cov=cov.astype(np.float64),
       fundamentals=clean_fundamentals,
       budget=1.0,
       risk_factor=0.5
)
    t2 = time.time()

    # ── Postprocess ──────────────────────────────────────────
    compile_results(TICKERS, weights, mu, cov)
    plot_weights(TICKERS, weights)
    t3 = time.time()

    # ── Timings ─────────────────────────────────────────────
    print(f"\nTiming Summary:")
    print(f"Fetch + preprocess : {t1-t0:.2f}s")
    print(f"VQE run            : {t2-t1:.2f}s")
    print(f"Postproc + display : {t3-t2:.2f}s")