# VQE Portfolio Optimizer: Quantum-Enhanced Financial Strategy

The **VQE Portfolio Optimizer** project uses the **Variational Quantum Eigensolver (VQE)** algorithm to solve the **Portfolio Optimization** problem. By treating financial risk and return objectives as a quantum system's Hamiltonian, this system leverages quantum computing techniques to identify optimal asset allocation, serving the results through a robust **FastAPI** backend.

---

## 1. Project Overview and Quantum Approach

The core idea is to map the complex, high-dimensional portfolio optimization challenge onto a quantum circuit.

### 1.1 VQE in Quantum Finance

VQE is a hybrid quantum-classical algorithm used to find the minimum energy state (ground state) of a system. For portfolio optimization, this means finding the portfolio weights that minimize risk for a given expected return:

1.  **Define the Hamiltonian:** The objective function (e.g., minimizing volatility and transaction costs) is encoded as the quantum **Hamiltonian**.
2.  **Initialize the Ansatz:** A parameterized quantum circuit (the Ansatz) is used to prepare quantum states that represent different portfolio weightings.
3.  **Classical Optimization:** A classical optimizer iteratively adjusts the circuit parameters to minimize the Hamiltonian's expectation value (the "energy"), which corresponds to the **optimal portfolio weights**.

---

## 2. System Architecture

The project is structured around a sequential data pipeline feeding into a quantum processing unit and a FastAPI server.

| Component | Description | Key Files/Directories |
| :--- | :--- | :--- |
| **Data Fetching** | Retrieves historical market data and comprehensive financial fundamentals using `yfinance`. | `preprocessing/fetch_data.py`, `preprocessing/fetch_fundamentals.py` |
| **Quantum Core** | Implements the VQE algorithm using **Qiskit** to calculate optimal portfolio weights. | `processing/vqe_portfolio.py`, `run_all.py` |
| **Backend API** | A **FastAPI** application to handle requests, run optimizations, and serve results via a REST API. | `Backend_Server/main.py` |
| **Post-processing** | Analyzes and visualizes the VQE results for performance metrics. | `postprocessing/analyze.py`, `postprocessing/visualize.py` |

---

## 3. Execution Guide

### Prerequisites

* Python (3.x)
* Node.js/npm (for the optional Frontend UI)
* Git

### Step-by-Step Execution

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/ManthriParthiv/fastapi-stock-app.git](https://github.com/ManthriParthiv/fastapi-stock-app.git)
    cd fastapi-stock-app
    ```

2.  **Install Dependencies:**
    ```bash
    # Install all necessary packages, including Qiskit, FastAPI, and yfinance
    pip install -r Backend_Server/quantum_optimizer/requirements.txt
    ```

3.  **Data Preparation:**
    Execute the data pipeline to populate the local `data/` directory.
    ```bash
    cd Backend_Server/quantum_optimizer
    python -m preprocessing.fetch_data.py
    python -m preprocessing.fetch_fundamentals.py
    python -m preprocessing.parallel_fetch.py
    ```

4.  **Start Backend Server:**
    Run the FastAPI application.
    ```bash
    cd ../../Backend_Server
    uvicorn main:app --reload
    ```
    * **Backend API:** `http://localhost:8000`
    * **API Documentation (Swagger UI):** `http://localhost:8000/docs`

5.  **Start Frontend UI (Optional, in a new terminal):**
    ```bash
    cd ../frontend_UI/Stocks_App
    npm install
    npm run dev
    ```
    * **Frontend UI:** `http://localhost:3000`

---

## 4. Key Dependencies and Financial Parameters

### 4.1 Core Dependencies

| Package | Version | Purpose |
| :--- | :--- | :--- |
| **`qiskit`** | `>0.46.0,<0.47.0` | Primary quantum computing framework. |
| **`qiskit-algorithms`** | | Provides the VQE implementation. |
| **`fastapi`** | `==0.110.1` | High-performance Python web framework. |
| **`yfinance`** | `==0.2.40` | Financial data source. |

### 4.2 Comprehensive Financial Parameters

The system fetches and analyzes **16 fundamental parameters** to enrich the optimization model:

* P/E Ratio, P/B Ratio, Debt-to-Equity (D/E), Research & Development Expenditure (RDE), Current Ratio, Dividend Payout (`payoutRatio`), and more.
* **Key Value Metrics:** **EV/EBITDA**, **Beta**, **MarketCap**, **revenueGrowth**, **pegRatio**, and **profitMargins**.
* **Additional Metrics:** **Free Cash Flow** (`freeCashflow`), **Operating Margin** (`operatingMargins`), **P/S Ratio** (`priceToSalesTrailing12Months`), and **Current Ratio** (`currentRatio`).

---

## 5. API Endpoints and Example

### Key Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/optimize` | Executes the VQE portfolio optimization based on user inputs. |
| `GET` | `/results` | Retrieves the latest portfolio weights and metrics. |

### Example Optimization Request

The `/optimize` endpoint accepts a JSON body defining the constraints:

```json
{
  "tickers": ["TCS.NS", "SIEMENS.NS"],
  "risk_factor": 0.6,    
  "budget": 1.0,         
  "strategy": "balanced" 
}
