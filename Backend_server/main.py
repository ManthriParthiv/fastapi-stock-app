from fastapi import FastAPI, Query, HTTPException, APIRouter
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from http import HTTPStatus
import yfinance as yf
import pandas as pd
import math
from pydantic import BaseModel,Field
from typing import List, Dict, Any
import numpy as np
import logging
from pathlib import Path

# ---------- Import tickers and init core app ----------
from tickers import tickers

app = FastAPI(title="Quantum Optimizer", version="1.0.0")

# ✅ CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Load tickers and stock data
df, tickers = tickers()


# ---------- Helper Functions ----------
def safe_value(val):
    """Handle NaN/inf values."""
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None
    return val


# ---------- Stock Routes (Original main.py) ----------
@app.get("/", status_code=HTTPStatus.OK)
def home():
    return {"message": "Stock API: Stocks + Quantum Optimization"}


@app.get("/stocks", status_code=HTTPStatus.OK)
def get_stocks(page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=500)):
    start = (page - 1) * limit
    end = start + limit
    if start >= len(df):
        raise HTTPException(status_code=404, detail="No more stocks available.")

    result = [
        {"ticker": safe_value(row["Symbol"]), "name": safe_value(row["Name"])}
        for _, row in df.iloc[start:end].iterrows()
    ]
    return JSONResponse(content=result)


@app.get("/stock/{ticker}", status_code=HTTPStatus.OK)
async def get_one_stock(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "ticker": ticker,
            "price": safe_value(info.get("currentPrice")),
            "volume": safe_value(info.get("volume")),
            "link": f"https://finance.yahoo.com/quote/{ticker}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching data: {str(e)}")


# ---------- Quantum Router (Converted fastapi_adapter.py) ----------

quantum_router = APIRouter(prefix="/quantum")

class PortfolioRequest(BaseModel):
    tickers: List[str] = Field(..., min_items=2, max_items=4)
    risk_factor: float = Field(0.5, ge=0.1, le=1.0)
    budget: float = Field(1.0, gt=0)

@quantum_router.get("/")
def quantum_root():
    return {"message": "Quantum Portfolio Optimizer Subsystem"}


@quantum_router.post("/optimize")
async def optimize(request: PortfolioRequest):
    try:
        # Load data (replace paths as needed)
        data_path = Path(__file__).parent/"quantum_optimizer"/"data"
        prices = pd.read_csv(data_path / "last6m.csv", index_col=0, parse_dates=True)[request.tickers]
        fundamentals = pd.read_csv(data_path / "fundamentals.csv", index_col="Ticker").loc[request.tickers]

        # Calculate returns and covariance
        returns = prices.pct_change().dropna()
        mu = returns.mean().values.astype(np.float64)
        cov = returns.cov().values.astype(np.float64)

        # Run VQE (import your actual function)
        from quantum_optimizer.processing.vqe_portfolio import run_vqe
        weights, _ = run_vqe(mu=mu, cov=cov, fundamentals=fundamentals, budget=request.budget,
                             risk_factor=request.risk_factor)

        return {
            "tickers": request.tickers,
            "weights": {t: float(w) for t, w in zip(request.tickers, weights)},
            "risk": float(np.sqrt(weights @ cov @ weights.T))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@quantum_router.get("/health")
def health_check():
    return {"status": "healthy"}


# ---------- Mount Quantum Router ----------
app.include_router(quantum_router)


# ---------- VQE Endpoint (Original main.py) ----------
class VQEInput(BaseModel):
    mu: List[float]
    cov: List[List[float]]
    fundamentals: List[float]
    budget: float
    risk_factor: float


@app.post("/quantum/portfolio-optimize")
def optimize_portfolio(request: VQEInput):
    try:
        result = run_quantum_backend(**request.dict())
        return {"optimized_weights": result["weights"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Run Server ----------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)