from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field  
import numpy as np
import pandas as pd
from typing import Dict, List
import logging
from pathlib import Path




# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Quantum Portfolio Optimizer", version="1.0.0")

class PortfolioRequest(BaseModel):
    tickers: List[str] = Field(..., min_items=2, max_items=4)
    risk_factor: float = Field(0.5, ge=0.1, le=1.0)
    budget: float = Field(1.0, gt=0)

@app.get("/")
def first():
    return{"data":"you are viewing fastapi_adapter server"}

@app.post("/optimize")
async def optimize(request: PortfolioRequest):
    try:
        logger.info(f"Starting optimization for {request.tickers}")
        
        # 1. Load data
        data_path = Path(__file__).parent.parent/"quantum_optimizer"/"data"
        prices = pd.read_csv(
            data_path/"last6m.csv",
            index_col=0,
            parse_dates=True
        )[request.tickers]
        
        fundamentals = pd.read_csv(
            data_path/"fundamentals.csv",
            index_col="Ticker"
        ).loc[request.tickers]

        # 2. Clean and prepare data
        returns = prices.pct_change().dropna()
        mu = returns.mean().values.astype(np.float64)
        cov = returns.cov().values.astype(np.float64)
        
        clean_fundamentals = {
            t: {
                'PE': 1.0 if np.isnan(fundamentals.at[t, 'PE']) else float(fundamentals.at[t, 'PE']),
                'PB': 1.0 if np.isnan(fundamentals.at[t, 'PB']) else float(fundamentals.at[t, 'PB']),
                'ROE': 0.1 if np.isnan(fundamentals.at[t, 'ROE']) else float(fundamentals.at[t, 'ROE'])
            }
            for t in request.tickers
        }

        # 3. Run VQE
        from quantum_optimizer.processing.vqe_portfolio import run_vqe
        weights, _ = run_vqe(
            mu=mu,
            cov=cov,
            fundamentals=clean_fundamentals,
            budget=request.budget,
            risk_factor=request.risk_factor
        )
        
        return {
            "tickers": request.tickers,
            "weights": {t: float(w) for t, w in zip(request.tickers, weights)},
            "risk": float(np.sqrt(weights @ cov @ weights.T)),
            "return": float(weights @ mu),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Optimization failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Optimization failed: {str(e)}"
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}