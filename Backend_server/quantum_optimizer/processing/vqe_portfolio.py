import numpy as np
from qiskit.quantum_info import SparsePauliOp
from qiskit.circuit.library import RealAmplitudes
from qiskit_algorithms import VQE
from qiskit_algorithms.optimizers import SPSA
from qiskit.primitives import Estimator
from typing import Dict

def create_hamiltonian(mu, cov, fundamentals, risk_factor, budget):
    """Create Hamiltonian with guaranteed real coefficients"""
    n = len(mu)
    terms = []
    
    # Clean and order fundamentals
    tickers = sorted(fundamentals.keys())
    pe_ratios = np.array([
        float(fundamentals[t].get('PE', 1.0)) if not np.isnan(fundamentals[t].get('PE', 1.0))
        else 1.0  # Default value for NaN
        for t in tickers
    ])
    
    # Quadratic terms (risk)
    for i in range(n):
        for j in range(i, n):
            pauli = ['I']*n
            pauli[i] = 'Z'
            pauli[j] = 'Z'
            coeff = float(np.real(risk_factor * cov[i,j]))  # Force real
            terms.append((''.join(pauli), coeff))
    
    # Linear terms (return)
    for i in range(n):
        pauli = ['I']*n
        pauli[i] = 'Z'
        coeff = float(np.real(-mu[i] * pe_ratios[i]))  # Force real
        terms.append((''.join(pauli), coeff))
    
    # Budget constraint
    for i in range(n):
        pauli = ['I']*n
        pauli[i] = 'Z'
        terms.append((''.join(pauli), float(0.1 * budget)))
    
    # Identity term
    terms.append(('I'*n, float(0.5 * n)))
    
    # Final validation
    for p, c in terms:
        if not isinstance(c, float):
            raise ValueError(f"Coefficient {c} for {p} is not float")
        if np.iscomplex(c):
            raise ValueError(f"Complex coefficient {c} detected")
    
    return SparsePauliOp.from_list(terms)

def run_vqe(mu, cov, fundamentals, budget, risk_factor, maxiter=50):
    """Robust VQE implementation with complete error handling"""
    try:
        # Input validation
        mu = np.array(mu, dtype=np.float64).flatten()
        cov = np.array(cov, dtype=np.float64)
        n = len(mu)
        
        # Clean fundamentals
        clean_fundamentals = {
            t: {
                'PE': float(fundamentals[t].get('PE', 1.0)) if not np.isnan(fundamentals[t].get('PE', 1.0)) else 1.0,
                'PB': float(fundamentals[t].get('PB', 1.0)) if not np.isnan(fundamentals[t].get('PB', 1.0)) else 1.0,
                'ROE': float(fundamentals[t].get('ROE', 0.1)) if not np.isnan(fundamentals[t].get('ROE', 0.1)) else 0.1
            }
            for t in fundamentals
        }
        
        # Build Hamiltonian
        H = create_hamiltonian(mu, cov, clean_fundamentals, risk_factor, budget)
        
        # Quantum circuit setup
        ansatz = RealAmplitudes(n, reps=1, entanglement='linear', insert_barriers=True)
        optimizer = SPSA(maxiter=maxiter, learning_rate=0.01, perturbation=0.01)
        
        # Run VQE
        vqe = VQE(
            estimator=Estimator(),
            ansatz=ansatz,
            optimizer=optimizer,
            initial_point=np.random.rand(ansatz.num_parameters)
        )
        result = vqe.compute_minimum_eigenvalue(H)
        
        # Process results
        theta = np.real(result.optimal_point)  # Force real
        weights = np.sin(theta[:n])**2
        weights = np.real(weights / np.sum(weights))  # Normalize and ensure real
        
        return weights, result
        
    except Exception as e:
        raise RuntimeError(f"VQE failed: {str(e)}\n"
                         f"mu: {mu}\n"
                         f"cov: {cov}\n"
                         f"fundamentals: {fundamentals}")