# quantum_optimizer/api.py

import pandas as pd
import numpy as np

from .processing.utils import load_returns, load_features, annualize
from .processing.vqe_portfolio import run_vqe

def run_quantum_backend(mu=None, cov=None, fundamentals=None, budget=1.0, risk_factor=0.5):
    """
    API-friendly wrapper that runs the full VQE portfolio pipeline.
    
    Either:
    - Pass all inputs (mu, cov, fundamentals) manually, OR
    - Leave them as None and data will be auto-loaded from CSVs.
    """
    if mu is None or cov is None or fundamentals is None:
        # Load default files (as in run_all.py)
        TICKERS = ["TCS.NS", "SIEMENS.NS", "NHPC.NS", "IDEA.NS"]
        CSV_PATH = "data/last6m.csv"
        FUND_CSV = "data/fundamentals.csv"

        print("🔄 Auto-loading data from CSV...")
        features = load_features(CSV_PATH, FUND_CSV)
        mu, cov = annualize(load_returns(CSV_PATH))
        fundamentals = [1] * len(TICKERS)  # Or extract from features if needed

    # Ensure inputs are NumPy arrays
    mu = np.array(mu)
    cov = np.array(cov)
    fundamentals = np.array(fundamentals)
    if len(mu) != len(fundamentals):
        raise ValueError(f"mu and fundamentals must be of same length, got {len(mu)} and {len(fundamentals)}")
    if cov.shape != (len(mu), len(mu)):
        raise ValueError(f"cov must be a square matrix of shape ({len(mu)}, {len(mu)}), got {cov.shape}")

    weights, result = run_vqe(
        mu=mu,
        cov=cov,
        fundamentals=fundamentals,
        budget=budget,
        risk_factor=risk_factor,
    )

    return {
        "weights": weights.tolist(),
        "energy": result.optimal_value,
        "theta": result.optimal_point.tolist(),
        "num_iterations": result.optimizer_evals
    }
