import os
import time
import pandas as pd
import numpy as np
from typing import List, Dict
from preprocessing.fetch_data import fetch_and_cache   
from processing.utils import load_returns, load_features, annualize
from processing.vqe_portfolio import run_vqe
from postprocessing.analyze import compile_results
from postprocessing.visualize import plot_weights

# Default values when data is missing
DEFAULT_VALUES = {
    'PE': 15.0,
    'PB': 3.0,
    'ROE': 0.15,
    'EV/EBITDA': 12.0,
    'RevenueGrowth': 0.05,
    'PEGRatio': 1.0,
    'NetMargin': 0.1,
    'FreeCF': 0.0,
    'OpMargin': 0.15,
    'P/S': 2.0,
    'Payout': 0.3,
    'CurrRatio': 1.5
}

def load_fundamentals_as_dict(tickers: List[str], csv_path: str) -> Dict[str, Dict[str, float]]:
    """Load fundamentals with proper error handling and defaults"""
    try:
        df = pd.read_csv(csv_path)
        if 'Ticker' not in df.columns:
            df = pd.read_csv(csv_path, index_col=0)
        
        fundamentals = {}
        for t in tickers:
            try:
                if t in df.index:
                    row = df.loc[t]
                else:
                    row = df[df['Ticker'] == t].iloc[0]
                
                fundamentals[t] = {
                    param: float(row[param]) if param in row and not pd.isna(row[param]) 
                    else DEFAULT_VALUES[param]
                    for param in DEFAULT_VALUES.keys()
                }
            except Exception as e:
                print(f"⚠️ Warning: Using defaults for {t} due to: {str(e)}")
                fundamentals[t] = DEFAULT_VALUES.copy()
        
        return fundamentals
    
    except Exception as e:
        print(f"⚠️ Warning: Using all defaults due to: {str(e)}")
        return {t: DEFAULT_VALUES.copy() for t in tickers}

if __name__ == "__main__":
    TICKERS = ["TCS.NS", "SIEMENS.NS", "NHPC.NS", "IDEA.NS"]
    CSV_PATH = "data/last6m.csv"
    FUND_CSV = "data/fundamentals.csv"

    t0 = time.time()
    
    # ── Prices ────────────────────────────────────────────────
    if os.path.exists(CSV_PATH):
        print(f"⏩ Loading cached prices from {CSV_PATH}")
        prices = pd.read_csv(CSV_PATH, index_col=0, parse_dates=True)
    else:
        print("⏳ Cache miss – fetching prices …")
        from preprocessing.parallel_fetch import parallel_fetch
        groups = [[t] for t in TICKERS]
        outpaths = [f"data/{t}.csv" for t in TICKERS]
        fetched = parallel_fetch(groups, outpaths, period="6mo", max_workers=4)
        prices = pd.concat(fetched.values(), axis=1)
        prices.to_csv(CSV_PATH)
    print("Prices shape:", prices.shape)

    # ── Fundamentals ─────────────────────────────────────────
    if os.path.exists(FUND_CSV):
        print(f"⏩ Loading cached fundamentals from {FUND_CSV}")
        fundamentals = load_fundamentals_as_dict(TICKERS, FUND_CSV)
    else:
        print("⏳ Cache miss – fetching fundamentals …")
        from preprocessing.fetch_fundamentals import fetch_fundamentals
        fetch_fundamentals(TICKERS, FUND_CSV)
        fundamentals = load_fundamentals_as_dict(TICKERS, FUND_CSV)

    # ── Data Preparation ────────────────────────────────────
    returns = load_returns(CSV_PATH)  # Pass the file path as expected by load_returns
    mu, cov = annualize(returns)
    t1 = time.time()

    # Data validation
    print("\nData Validation:")
    print(f"mu shape: {mu.shape}, type: {mu.dtype}")
    print(f"cov shape: {cov.shape}, type: {cov.dtype}")
    print("Sample PE values:", [fundamentals[t].get('PE', 'MISSING') for t in TICKERS[:2]])
    
    # ── Run Optimization ─────────────────────────────────────
    try:
        weights, vqe_res = run_vqe(
            mu=mu,
            cov=cov,
            fundamentals=fundamentals,
            budget=1.0,
            risk_factor=0.5
        )
        t2 = time.time()

        # ── Postprocess ─────────────────────────────────────
        compile_results(TICKERS, weights, mu, cov)
        plot_weights(TICKERS, weights)
        
    except Exception as e:
        print(f"❌ Optimization failed: {str(e)}")
        weights = {t: 1.0/len(TICKERS) for t in TICKERS}  # Equal weights fallback
        print("⚠️ Using equal weights as fallback")
        t2 = time.time()

    # ── Timings ─────────────────────────────────────────────
    t3 = time.time()
    print(f"\nTiming Summary:")
    print(f"Data loading      : {(t1-t0):.2f}s")
    print(f"Optimization      : {(t2-t1):.2f}s")
    print(f"Post-processing   : {(t3-t2):.2f}s")
    print(f"Total             : {(t3-t0):.2f}s")