from fastapi import FastAPI, Query, HTTPException, APIRouter, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from http import HTTPStatus
import pandas as pd
import math
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import numpy as np
import logging
from pathlib import Path
import os

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("quantum-optimizer")

# ---------- Initialize FastAPI App ----------
app = FastAPI(
    title="Quantum Portfolio Optimizer",
    version="2.0.0",
    description="API for deterministic quantum portfolio optimization using NFT optimizer"
)

# ---------- CORS Configuration ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Data Loading ----------
try:
    from tickers import tickers
    data, df, available_tickers = tickers()
    logger.info(f"Loaded {len(available_tickers)} tickers")
except ImportError:
    logger.error("Failed to import tickers.py - using fallback data")
    data = pd.DataFrame({
        "Ticker": ["TCS.NS", "SIEMENS.NS"],
        "Name": ["TCS", "Siemens"]
    })
    df = data
    available_tickers = data["Ticker"].tolist()

# ---------- Helper Functions ----------
def safe_value(val: Any) -> Optional[float]:
    """Safely handle NaN/inf values in API responses."""
    if isinstance(val, (float, int)) and not math.isfinite(val):
        return None
    return val

# ---------- Core Stock Routes ----------
@app.get("/", status_code=HTTPStatus.OK)
def home():
    """Root endpoint with API information"""
    return {
        "message": "Quantum Stock Optimizer API",
        "endpoints": {
            "/stocks": "Browse available stocks",
            "/stock/{ticker}": "Get individual stock data",
            "/quantum/optimize": "Quantum portfolio optimization"
        }
    }

@app.get("/stocks", status_code=HTTPStatus.OK)
def get_stocks(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=500, description="Items per page")
):
    """Paginated list of available stocks"""
    start = (page - 1) * limit
    end = start + limit
    
    if start >= len(df):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="No more stocks available."
        )

    return JSONResponse(content=[
        {
            "ticker": safe_value(row["Ticker"]),
            "name": safe_value(row["Name"])
        } for _, row in df.iloc[start:end].iterrows()
    ])

@app.get("/stock/{ticker}", status_code=HTTPStatus.OK)
async def get_stock_data(ticker: str):
    """Get detailed information for a specific stock"""
    try:
        match = data.loc[data["Ticker"] == ticker]
        if match.empty:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Ticker {ticker} not found"
            )

        row = match.iloc[0].to_dict()
        return {k: safe_value(v) for k, v in row.items()}
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Error fetching data for {ticker}: {str(e)}"
        )

# ---------- Quantum Optimization Module ----------
quantum_router = APIRouter(prefix="/quantum", tags=["Quantum Optimization"])

class PortfolioRequest(BaseModel):
    """Request model for portfolio optimization"""
    tickers: List[str] = Field(
        ...,
        min_items=2,
        max_items=4,
        example=["TCS.NS", "SIEMENS.NS"],
        description="List of stock tickers to optimize"
    )
    risk_factor: float = Field(
        0.5, 
        ge=0.1, 
        le=1.0,
        description="Risk appetite (0.1=conservative to 1.0=aggressive)"
    )
    budget: float = Field(
        1.0,
        gt=0,
        description="Total investment budget"
    )

@quantum_router.post("/optimize", response_model=Dict[str, Any])
async def optimize_portfolio(request: PortfolioRequest):
    """
    Run deterministic quantum portfolio optimization using VQE with NFT optimizer
    
    Returns:
        weights: Dict of ticker to allocation percentage
        risk: Portfolio volatility
        expected_return: Expected portfolio return
        optimizer: Method used (NFT)
    """
    try:
        # Validate tickers
        invalid_tickers = set(request.tickers) - set(available_tickers)
        if invalid_tickers:
            raise ValueError(f"Invalid tickers: {invalid_tickers}")

        # Load data
        data_path = Path(__file__).parent/"quantum_optimizer"/"data"
        prices = pd.read_csv(
            data_path/"last6m.csv",
            index_col=0,
            parse_dates=True
        )[request.tickers]
        
        fundamentals = pd.read_csv(
            data_path/"fundamentals.csv",
            index_col="Ticker"
        ).loc[request.tickers].fillna(1.0)

        # Calculate metrics
        returns = prices.pct_change().dropna()
        mu = returns.mean().values.astype(np.float64)
        cov = returns.cov().values.astype(np.float64)

        # Run deterministic optimization
        from quantum_optimizer.processing.vqe_portfolio import run_vqe
        weights, _ = run_vqe(
            mu=mu,
            cov=cov,
            fundamentals=fundamentals.to_dict(orient='index'),
            budget=request.budget,
            risk_factor=request.risk_factor
        )

        # Calculate metrics
        portfolio_risk = float(np.sqrt(weights @ cov @ weights.T))
        expected_return = float(weights @ mu)

        return {
            "tickers": request.tickers,
            "weights": {t: float(w) for t, w in zip(request.tickers, weights)},
            "risk": portfolio_risk,
            "expected_return": expected_return,
            "optimizer": "NFT (Deterministic)",
            "status": "success"
        }

    except Exception as e:
        logger.error(f"Optimization failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Portfolio optimization failed: {str(e)}"
        )

# ---------- Mount All Routers ----------
app.include_router(quantum_router)

# ---------- Main Execution ----------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )