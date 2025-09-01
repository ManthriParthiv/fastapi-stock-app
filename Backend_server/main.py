from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict
import numpy as np
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime

app = FastAPI()
logger = logging.getLogger(__name__)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PortfolioRequest(BaseModel):
    tickers: List[str] = Field(..., min_items=2, max_items=10, 
                             description="List of tickers to optimize")
    risk_factor: float = Field(0.5, ge=0.1, le=1.0, 
                             description="Risk appetite (0.1-1.0)")
    budget: float = Field(1.0, gt=0, 
                        description="Total investment budget")
    use_fundamentals: bool = Field(True,
                                 description="Include fundamental analysis")

@app.post("/optimize")
async def optimize_portfolio(request: PortfolioRequest):
    """Optimize portfolio using quantum VQE with financial parameters"""
    try:
        logger.info(f"Optimization request for {request.tickers}")
        
        # Data loading
        data_path = Path(__file__).parent/"quantum_optimizer"/"data"
        
        # Load price data
        prices = pd.read_csv(
            data_path/"last6m.csv", 
            index_col=0, 
            parse_dates=True
        )[request.tickers]
        
        # Calculate returns (annualized)
        returns = prices.pct_change().dropna()
        mu = returns.mean().values * 252  # Annualize returns
        cov = returns.cov().values * 252  # Annualize covariance

        # Load fundamentals if needed
        fundamentals_dict = {}
        if request.use_fundamentals:
            try:
                fundamentals = pd.read_csv(
                    data_path/"fundamentals.csv",
                    index_col="Ticker"
                ).loc[request.tickers]
                
                fundamentals_dict = {
                    ticker: fundamentals.loc[ticker].to_dict()
                    for ticker in request.tickers
                }
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to load fundamentals: {str(e)}"
                )

        # Run quantum optimization
        from quantum_optimizer.processing.vqe_portfolio import run_vqe
        weights, result = run_vqe(
            mu=mu,
            cov=cov,
            fundamentals=fundamentals_dict,
            budget=request.budget,
            risk_factor=request.risk_factor
        )

        # Calculate portfolio metrics
        portfolio_return = float(weights @ mu)
        portfolio_risk = float(np.sqrt(weights @ cov @ weights.T))

        # Prepare response
        response = {
            "timestamp": datetime.utcnow().isoformat(),
            "tickers": request.tickers,
            "weights": {t: round(float(w), 4) for t, w in zip(request.tickers, weights)},
            "risk": round(portfolio_risk, 6),
            "expected_return": round(portfolio_risk, 6),
            "fundamentals_used": request.use_fundamentals,
            "parameter_values": result.get('raw_fundamentals', {}),
            "composite_scores": result.get('composite_scores', {}),
            "optimization_metadata": result.get('optimizer_metadata', {})
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Optimization failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Portfolio optimization failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)