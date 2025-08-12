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
from datetime import datetime

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("quantum-optimizer")

# ---------- Initialize FastAPI App ----------
app = FastAPI(
    title="Quantum Portfolio Optimizer",
    version="2.2.0",
    description="API for quantum portfolio optimization with fundamental analysis",
    docs_url="/docs",
    redoc_url="/redoc"
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
        "Ticker": ["TCS.NS", "SIEMENS.NS", "NHPC.NS", "IDEA.NS"],
        "Name": ["TCS", "Siemens", "NHPC", "Idea Cellular"]
    })
    df = data
    available_tickers = data["Ticker"].tolist()

# Financial parameter definitions
FINANCIAL_METRICS = {
    'PE': {'default': 15.0, 'desc': 'Price-to-Earnings ratio'},
    'PB': {'default': 3.0, 'desc': 'Price-to-Book ratio'},
    'ROE': {'default': 0.15, 'desc': 'Return on Equity'},
    'Volume': {'default': 0, 'desc': 'Trading volume'},
    'EarningsDate': {'default': '', 'desc': 'Upcoming earnings date'},
    'EV_EBITDA': {'default': 12.0, 'desc': 'Enterprise Value to EBITDA'},
    'Beta': {'default': 1.0, 'desc': 'Stock volatility relative to market'},
    'RevenueGrowth': {'default': 0.05, 'desc': 'Yearly revenue growth rate'},
    'PEGRatio': {'default': 1.0, 'desc': 'PE divided by earnings growth rate'},
    'NetMargin': {'default': 0.1, 'desc': 'Net profit margin'},
    'FreeCF': {'default': 0.0, 'desc': 'Free cash flow'},
    'OpMargin': {'default': 0.15, 'desc': 'Operating profit margin'},
    'PS': {'default': 2.0, 'desc': 'Price-to-Sales ratio'},
    'Payout': {'default': 0.3, 'desc': 'Dividend payout ratio'},
    'CurrRatio': {'default': 1.5, 'desc': 'Current ratio'}
}

FINANCIAL_DEFAULTS = {k: v['default'] for k, v in FINANCIAL_METRICS.items()}

def safe_value(val: Any) -> Optional[float]:
    """Safely handle NaN/inf values in API responses."""
    if isinstance(val, (float, int)) and not math.isfinite(val):
        return None
    return float(val) if isinstance(val, (float, int)) else val

# ---------- Core Stock Routes ----------
@app.get("/", status_code=HTTPStatus.OK)
def home():
    return {
        "message": "Quantum Stock Optimizer API",
        "version": app.version,
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "/stocks": "Browse available stocks",
            "/stock/{ticker}": "Get individual stock data",
            "/quantum/optimize": "Quantum portfolio optimization",
            "/metrics": "List available financial metrics"
        }
    }

@app.get("/metrics", status_code=HTTPStatus.OK)
def list_financial_metrics():
    """List all available financial metrics with descriptions"""
    return JSONResponse(content=FINANCIAL_METRICS)

@app.get("/stocks", status_code=HTTPStatus.OK)
def get_stocks(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=500, description="Items per page"),
    min_pe: float = Query(None, ge=0, description="Filter by minimum PE ratio"),
    max_pe: float = Query(None, ge=0, description="Filter by maximum PE ratio")
):
    """Paginated list of available stocks with basic financial metrics"""
    filtered_df = df.copy()
    
    if min_pe is not None:
        filtered_df = filtered_df[filtered_df['PE'] >= min_pe]
    if max_pe is not None:
        filtered_df = filtered_df[filtered_df['PE'] <= max_pe]
    
    start = (page - 1) * limit
    end = start + limit
    
    if start >= len(filtered_df):
        raise HTTPException(status_code=404, detail="No more stocks available.")

    return JSONResponse(content=[
        {
            "ticker": safe_value(row["Ticker"]),
            "name": safe_value(row["Name"]),
            "pe": safe_value(row.get("PE")),
            "pb": safe_value(row.get("PB"))
        } for _, row in filtered_df.iloc[start:end].iterrows()
    ])

@app.get("/stock/{ticker}", status_code=HTTPStatus.OK)
async def get_stock_data(ticker: str):
    """Get complete fundamental data for a specific stock"""
    try:
        match = data.loc[data["Ticker"] == ticker.upper()]
        if match.empty:
            raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found")

        # Load fundamentals data
        data_path = Path(__file__).parent/"quantum_optimizer"/"data"
        fundamentals = pd.read_csv(
            data_path/"fundamentals.csv",
            index_col="Ticker"
        )
        
        # Add missing columns with default values
        for metric, config in FINANCIAL_METRICS.items():
            if metric not in fundamentals.columns and metric != 'EarningsDate':
                fundamentals[metric] = config['default']
        
        if 'EarningsDate' in fundamentals.columns:
            fundamentals['EarningsDate'] = fundamentals['EarningsDate'].fillna('')
        else:
            fundamentals['EarningsDate'] = ''
        
        row = match.iloc[0].to_dict()
        fundamentals_row = fundamentals.loc[ticker.upper()].to_dict()

        return {
            "ticker": ticker.upper(),
            "name": row.get("Name"),
            "fundamentals": {
                metric: safe_value(fundamentals_row.get(metric))
                for metric in FINANCIAL_METRICS.keys()
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# ---------- Quantum Optimization ----------
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
    strategy: str = Field(
        "balanced",
        description="Investment strategy: conservative/balanced/aggressive"
    )
    fundamental_weights: Optional[Dict[str, float]] = Field(
        None,
        description="Optional weights for financial metrics (sum should be <= 1)"
    )

@quantum_router.post("/optimize", response_model=Dict[str, Any])
async def optimize_portfolio(request: PortfolioRequest):
    """
    Run quantum portfolio optimization with fundamental analysis
    
    Returns:
        - Portfolio weights
        - Risk and return metrics
        - Complete fundamental data for each stock
        - Optimization metadata
    """
    try:
        # Validate tickers
        invalid_tickers = set(request.tickers) - set(available_tickers)
        if invalid_tickers:
            raise ValueError(f"Invalid tickers: {', '.join(invalid_tickers)}")

        # Load data
        data_path = Path(__file__).parent/"quantum_optimizer"/"data"
        prices = pd.read_csv(
            data_path/"last6m.csv", 
            index_col=0,
            parse_dates=True
        )[request.tickers]
        
        # Load and prepare fundamentals data
        fundamentals = pd.read_csv(
            data_path/"fundamentals.csv",
            index_col="Ticker"
        )
        
        # Add missing columns with default values
        for metric, config in FINANCIAL_METRICS.items():
            if metric not in fundamentals.columns and metric != 'EarningsDate':
                fundamentals[metric] = config['default']
        
        if 'EarningsDate' in fundamentals.columns:
            fundamentals['EarningsDate'] = fundamentals['EarningsDate'].fillna('')
        else:
            fundamentals['EarningsDate'] = ''
        
        fundamentals = fundamentals.loc[request.tickers].fillna(FINANCIAL_DEFAULTS)

        # Apply fundamental weights if provided
        if request.fundamental_weights:
            total_weight = sum(request.fundamental_weights.values())
            if total_weight > 1.0:
                raise ValueError("Sum of fundamental weights cannot exceed 1.0")
            
            normalized_weights = {k: v/total_weight for k, v in request.fundamental_weights.items()}
            for metric, weight in normalized_weights.items():
                if metric in fundamentals.columns:
                    fundamentals[metric] = fundamentals[metric] * weight

        # Calculate returns
        returns = prices.pct_change().dropna()
        mu = returns.mean().values.astype(np.float64)
        cov = returns.cov().values.astype(np.float64)

        # Adjust risk factor based on strategy
        effective_risk_factor = request.risk_factor
        if request.strategy == "conservative":
            effective_risk_factor = max(0.1, request.risk_factor * 0.7)
        elif request.strategy == "aggressive":
            effective_risk_factor = min(1.0, request.risk_factor * 1.3)

        # Run optimization
        from quantum_optimizer.processing.vqe_portfolio import run_vqe
        weights, result = run_vqe(
            mu=mu,
            cov=cov,
            fundamentals=fundamentals.to_dict(orient='index'),
            budget=request.budget,
            risk_factor=effective_risk_factor
        )

        # Prepare comprehensive response
        response = {
            "tickers": request.tickers,
            "weights": {t: float(w) for t, w in zip(request.tickers, weights)},
            "risk": float(np.sqrt(weights @ cov @ weights.T)),
            "expected_return": float(weights @ mu),
            "fundamentals": {
                ticker: {
                    metric: safe_value(fundamentals.loc[ticker, metric])
                    for metric in FINANCIAL_METRICS.keys()
                }
                for ticker in request.tickers
            },
            "optimization_metadata": {
                "strategy": request.strategy,
                "effective_risk_factor": effective_risk_factor,
                "optimizer": "NFT",
                "timestamp": datetime.utcnow().isoformat()
            },
            "status": "success"
        }

        if request.budget != 1.0:
            response["investment_allocation"] = {
                ticker: round(float(w) * request.budget, 2)
                for ticker, w in zip(request.tickers, weights)
            }

        return response

    except Exception as e:
        logger.error(f"Optimization failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "solution": "Check ticker symbols or try different parameters",
                "documentation": "/docs#/Quantum%20Optimization/optimize_quantum_optimize_post"
            }
        )

app.include_router(quantum_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)