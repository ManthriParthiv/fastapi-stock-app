import pandas as pd
import yfinance as yf
import numpy as np
import requests
import json

# 1. Load first 3 tickers from CSV
df = pd.read_csv("Backend_server/tickers_with_names.csv")  # Adjust path if needed
tickers = df["Symbol"].dropna().unique()[:3]
print("Using tickers:", tickers)

# 2. Download stock data (last 6 months)
data = yf.download(tickers.tolist(), period="6mo", auto_adjust=True)

# 3. Calculate expected returns (mean) and covariance
returns = data.pct_change().dropna()
mu = returns.mean().tolist()
cov = returns.cov().values.tolist()

# 4. Dummy fundamentals (e.g., all 1s or PE ratio if available)
fundamentals = [1 for _ in range(len(tickers))]  # Replace with real data later
budget = 1.0
risk_factor = 0.5

# 5. Prepare request body
payload = {
    "mu": mu,
    "cov": cov,
    "fundamentals": fundamentals,
    "budget": budget,
    "risk_factor": risk_factor
}

# 6. Send POST request to FastAPI
response = requests.post("http://127.0.0.1:8000/quantum/portfolio-optimize", json=payload)

# 7. Print result
if response.status_code == 200:
    print("✅ Optimization Success!")
    print(json.dumps(response.json(), indent=2))
else:
    print("❌ Failed:", response.status_code, response.text)
