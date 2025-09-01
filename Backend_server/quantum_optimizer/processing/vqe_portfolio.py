import numpy as np
from qiskit.quantum_info import SparsePauliOp
from qiskit.circuit.library import RealAmplitudes
from qiskit_algorithms import VQE
from qiskit_algorithms.optimizers import NFT
from qiskit.primitives import Estimator
from typing import Dict, Tuple
import logging
from sklearn.preprocessing import MinMaxScaler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Financial parameter weights
PARAM_WEIGHTS = {
    'PE': 0.15, 'PB': 0.10, 'ROE': 0.10, 'EV/EBITDA': 0.12,
    'RevenueGrowth': 0.05, 'PEGRatio': 0.08, 'NetMargin': 0.10,
    'FreeCF': 0.10, 'OpMargin': 0.10, 'P/S': 0.10, 'Payout': 0.05,
    'CurrRatio': 0.05
}

def normalize_value(param: str, value: float) -> float:
    """Normalize financial metrics appropriately"""
    if param in ['PE', 'PB', 'EV/EBITDA', 'P/S', 'PEGRatio']:
        return 1/max(value, 0.1)  # Avoid division by zero
    elif param == 'FreeCF':
        return np.log1p(abs(value)) * (1 if value >=0 else -1)
    return value

def calculate_composite_score(params: Dict) -> float:
    """Calculate weighted score from fundamental parameters"""
    score = 0.0
    for param, weight in PARAM_WEIGHTS.items():
        value = params.get(param, 0)
        normalized = normalize_value(param, value)
        score += float(normalized) * weight
    return min(max(score * 100, 0), 100)  # Scale to 0-100 range

def create_hamiltonian(mu: np.ndarray, 
                      cov: np.ndarray, 
                      fundamentals: Dict,
                      risk_factor: float,
                      budget: float) -> SparsePauliOp:
    """Create Hamiltonian with financial parameters"""
    tickers = sorted(fundamentals.keys())
    # Align mu and cov to tickers order
    ticker_indices = {t: i for i, t in enumerate(tickers)}
    # If mu/cov are pandas objects with tickers as index/columns, align them
    import pandas as pd
    if isinstance(mu, pd.Series):
        mu = mu.loc[tickers].values
    if isinstance(cov, pd.DataFrame):
        cov = cov.loc[tickers, tickers].values
    n = len(tickers)
    terms = []
    # Calculate and normalize composite scores
    composite_scores = np.array([
        calculate_composite_score(fundamentals[t])/100
        for t in tickers
    ])
    scaler = MinMaxScaler()
    normalized_scores = scaler.fit_transform(composite_scores.reshape(-1, 1)).flatten()

    # Hamiltonian terms
    for i in range(n):
        for j in range(i, n):
            terms.append(
                (
                    ''.join(
                        ['I'] * i +
                        ['Z'] +
                        ['I'] * (j - i - 1 if j > i else 0) +
                        (['Z'] if j != i else []) +
                        ['I'] * (n - j - 1)
                    ),
                    float(risk_factor * cov[i, j])
                )
            )

        terms.append(
            (
                ''.join(['I'] * i + ['Z'] + ['I'] * (n - i - 1)),
                float(-mu[i] * normalized_scores[i] + 0.1 * budget)
            )
        )

    terms.append(('I'*n, float(0.5 * n)))
    return SparsePauliOp.from_list(terms)

def run_vqe(mu: np.ndarray, 
           cov: np.ndarray, 
           fundamentals: Dict,
           budget: float,
           risk_factor: float,
           maxiter: int = 200) -> Tuple[np.ndarray, Dict]:
    """Run VQE optimization with financial parameters"""
    try:
        # Input validation and conversion
        mu = np.asarray(mu, dtype=np.float64).flatten()
        cov = np.asarray(cov, dtype=np.float64)
        n = len(mu)
        
        # Build Hamiltonian
        H = create_hamiltonian(mu, cov, fundamentals, risk_factor, budget)
        
        # Quantum circuit setup
        ansatz = RealAmplitudes(n, reps=2, entanglement='linear')
        optimizer = NFT(maxiter=maxiter)

        # Run VQE
        vqe = VQE(
            estimator=Estimator(),
            ansatz=ansatz,
            optimizer=optimizer
        )
        # After VQE is constructed, get the correct number of parameters from vqe.ansatz
        num_params = vqe.ansatz.num_parameters
        initial_point = np.random.uniform(0, 1, num_params)
        vqe.initial_point = initial_point
        result = vqe.compute_minimum_eigenvalue(H)
        
        # Process results
        theta = np.real(result.optimal_point)
        weights = np.sin(theta[:n])**2
        weights /= np.sum(weights)
        
        return weights, {
            'composite_scores': {
                t: calculate_composite_score(fundamentals[t]) 
                for t in sorted(fundamentals.keys())
            },
            'optimization_metadata': {
                'optimal_value': float(result.optimal_value),
                'optimizer_time': float(result.optimizer_time)
            }
        }
        
    except Exception as e:
        logger.error(f"VQE optimization failed: {str(e)}")
        raise ValueError(f"Optimization error: {str(e)}") from e