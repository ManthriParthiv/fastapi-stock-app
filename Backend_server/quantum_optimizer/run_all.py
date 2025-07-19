import os, time
import pandas as pd

from preprocessing.fetch_data import fetch_and_cache   
from processing.utils import load_returns, load_features, annualize
from processing.vqe_portfolio import run_vqe
from postprocessing.analyze    import compile_results
from postprocessing.visualize   import plot_weights

if __name__ == "__main__":
    TICKERS  = ["TCS.NS","SIEMENS.NS","NHPC.NS","IDEA.NS"]
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
        groups   = [[t] for t in TICKERS]
        outpaths = [f"data/{t}.csv" for t in TICKERS]
        fetched = parallel_fetch(groups, outpaths, period="6mo", max_workers=4)
        df = pd.concat(fetched.values(), axis=1)
        df.to_csv(CSV_PATH)
    print("Prices shape:", df.shape)

    # ── Fundamentals ─────────────────────────────────────────
    if os.path.exists(FUND_CSV):
        print(f"⏩ Loading cached fundamentals from {FUND_CSV}")
    else:
        print("⏳ Cache miss – fetching fundamentals …")
        from preprocessing.fetch_fundamentals import fetch_fundamentals
        fetch_fundamentals(TICKERS, FUND_CSV)

    # build your features & stats
    features = load_features(CSV_PATH, FUND_CSV)
    mu, cov  = annualize(load_returns(CSV_PATH))
    t1 = time.time()

    # ── VQE ──────────────────────────────────────────────────
    weights, vqe_res = run_vqe(mu, cov, fundamentals=[1]*len(TICKERS),
                               budget=1.0, risk_factor=0.5)
    t2 = time.time()

    # ── Postprocess ──────────────────────────────────────────
    compile_results(TICKERS, weights, mu, cov)
    plot_weights(TICKERS, weights)
    t3 = time.time()

    # ── Timings ─────────────────────────────────────────────
    print(f"Fetch + preprocess : {t1-t0:.2f}s")
    print(f"VQE run            : {t2-t1:.2f}s")
    print(f"Postproc + display : {t3-t2:.2f}s")


































# WITHOUT CACHING
# # run_all.py

# import time
# import pandas as pd

# from preprocessing.parallel_fetch import parallel_fetch
# from preprocessing.fetch_fundamentals import fetch_fundamentals

# from processing.utils import load_returns, load_features, annualize
# from processing.vqe_portfolio import run_vqe

# from postprocessing.analyze import compile_results
# from postprocessing.visualize import plot_weights

# if __name__ == "__main__":
#     # ── Settings ───────────────────────────────────────────
#     TICKERS = ["TCS.NS", "SIEMENS.NS", "NHPC.NS", "IDEA.NS"]
#     CSV_PATH = "data/last6m.csv"
#     FUND_CSV = "data/fundamentals.csv"

#     # ── 1) Fetch & preprocess (parallel) ────────────────────
#     t0 = time.time()

#     # 1a) fetch each ticker into its own CSV in parallel
#     groups   = [[t] for t in TICKERS]
#     outpaths = [f"data/{t}.csv" for t in TICKERS]
#     fetched  = parallel_fetch(groups, outpaths, period="6mo", max_workers=4)

#     # 1b) stitch them back into one prices DataFrame
#     prices_df = pd.concat(fetched.values(), axis=1)
#     prices_df.to_csv(CSV_PATH)

#     # 1c) fetch fundamentals (P/E, P/B, ROE, Volume, EarningsDate)
#     fetch_fundamentals(TICKERS, FUND_CSV)

#     # 1d) load returns & fundamentals
#     mu, cov     = annualize(load_returns(CSV_PATH))
#     features_df = load_features(CSV_PATH, FUND_CSV)

#     # extract a single “fundamentals” vector in the same order as TICKERS:
#     # here we’ll just use P/E as our example feature
#     fund_df   = pd.read_csv(FUND_CSV, index_col=0)
#     fundamentals = fund_df.loc[TICKERS, "PE"].fillna(0).values

#     t1 = time.time()

#     # ── 2) Quantum VQE optimization ─────────────────────────
#     # run_vqe(mu, cov, fundamentals, risk_factor, budget)
#     weights, vqe_res = run_vqe(
#         mu              = mu,
#         cov             = cov,
#         fundamentals    = fundamentals,
#         risk_factor     = 0.5,
#         budget          = 1.0,
#     )
#     t2 = time.time()

#     # ── 3) Postprocess & display ────────────────────────────
#     compile_results(TICKERS, weights, mu, cov)
#     plot_weights(TICKERS, weights)
#     t3 = time.time()

#     # ── 4) Print timings ────────────────────────────────────
#     print("\n── TIMINGS ─────────────────────────────────────────")
#     print(f"Fetch + preprocess : {t1 - t0:.2f}s")
#     print(f"VQE run            : {t2 - t1:.2f}s")
#     print(f"Postproc + display : {t3 - t2:.2f}s")