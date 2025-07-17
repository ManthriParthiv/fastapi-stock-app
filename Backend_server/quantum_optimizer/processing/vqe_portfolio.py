import numpy as np
from qiskit.quantum_info import SparsePauliOp
from qiskit.circuit.library import RealAmplitudes
from qiskit_algorithms import VQE
from qiskit_algorithms.optimizers import SPSA
from qiskit.primitives import Estimator


def create_pauli_string(z_indices, num_qubits):
    """Return a length-n string of I/Z with Z’s at z_indices."""
    s = ["I"] * num_qubits
    for i in z_indices:
        s[i] = "Z"
    return "".join(s)


def create_hamiltonian(mu, cov, fundamentals, risk_factor, budget):
    """
    Build a SparsePauliOp representing:
    H = risk_factor * x^T Cov x
        - sum_i mu[i]*fundamentals[i]*x_i
        + budget penalty + identity offset
    """
    n = len(mu)
    terms = []

    # Quadratic (risk) terms
    for i in range(n):
        for j in range(i, n):
            coeff = risk_factor * cov[i, j]
            terms.append((create_pauli_string([i, j], n), coeff))

    # Linear (enhanced return)
    for i in range(n):
        coeff = -mu[i] * fundamentals[i]
        terms.append((create_pauli_string([i], n), coeff))

    # Budget penalty & identity
    for i in range(n):
        terms.append((create_pauli_string([i], n), 0.1 * budget))
    terms.append(("I" * n, 0.5 * n))

    pauli_list = [(p, float(c)) for p, c in terms]
    return SparsePauliOp.from_list(pauli_list)

def run_vqe(mu, cov, fundamentals, budget, risk_factor, maxiter=200):
    """
    1) Build H
    2) Prepare hardware-efficient ansatz
    3) Use SPSA + Estimator in VQE
    4) Extract optimal parameters → portfolio weights
    """
    n = len(mu)
    H = create_hamiltonian(mu, cov, fundamentals, risk_factor, budget)

    ansatz = RealAmplitudes(num_qubits=n, reps=2, entanglement="linear")
    optimizer = SPSA(maxiter=maxiter, learning_rate=0.05, perturbation=0.05)
    vqe = VQE(
        estimator=Estimator(),
        ansatz=ansatz,
        optimizer=optimizer,
        initial_point=np.random.rand(ansatz.num_parameters),
    )

    result = vqe.compute_minimum_eigenvalue(H)
    theta = result.optimal_point

    # 🛡️ Ensure theta has at least n values
    if len(theta) < n:
        raise ValueError(f"VQE returned {len(theta)} parameters, but {n} needed.")

    # map first n θ’s → x_i = sin(θ_i)^2, normalize
    w = np.sin(theta[:n]) ** 2
    w = w / w.sum()

    return w, result
