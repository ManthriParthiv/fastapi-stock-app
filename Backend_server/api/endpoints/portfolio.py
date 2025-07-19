from fastapi import APIRouter, HTTPException, Depends
import numpy as np
from typing import List
from ...quantum_optimizer.processing.vqe_portfolio import run_vqe
from ..dependencies import load_cached_data, VALID_TICKERS

router = APIRouter()

@router.post("/portfolio/optimize")
async def optimize_portfolio(tickers: List[str]):
    # 1. Validate tickers against your cache
    invalid = set(tickers) - VALID_TICKERS
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"These tickers aren't cached: {invalid}. Valid options: {VALID_TICKERS}"
        )

    # 2. Load your exact cached data
    data = load_cached_data()
    
    # 3. Prepare inputs for your existing run_vqe()
    price_matrix = data["prices"][tickers].values.astype(np.float64)
    fundamentals = data["fundamentals"].loc[tickers].to_dict(orient='index')

    # 4. Call your unmodified VQE function
    try:
        weights = run_vqe(price_matrix, **fundamentals)
        return {
            "success": True,
            "weights": {t: float(w) for t, w in zip(tickers, weights)},
            "cache_used": ["last6m.csv", "fundamentals.csv"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"VQE optimization failed: {str(e)}"
        )