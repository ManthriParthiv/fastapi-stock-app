from fastapi import FastAPI, Query, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from http import HTTPStatus
import yfinance as yf
import pandas as pd
import math
from pydantic import BaseModel
from typing import List, Dict, Any

from tickers import tickers  # Custom function/module that loads ticker CSV

app = FastAPI()

# ✅ CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Load tickers and stock data from CSV
df, tickers = tickers()

# ✅ Handle NaN, inf, etc.
def safe_value(val):
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None
    return val

@app.get("/", status_code=HTTPStatus.OK)
def home():
    return {"message": "📈 FastAPI Stock API — CSV list + Live details"}

# ✅ CSV-based paginated stock list
@app.get("/stocks", status_code=HTTPStatus.OK)
def get_stocks(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500)
):
    start = (page - 1) * limit
    end = start + limit
    if start >= len(df):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="No more stocks available for the requested page."
        )

    def clean(val):
        if pd.isna(val) or val in [float("inf"), float("-inf")]:
            return None
        return val

    result = [
        {
            "ticker": clean(row["Symbol"]),
            "name": clean(row["Name"]),
        }
        for _, row in df.iloc[start:end].iterrows()
    ]
    return JSONResponse(status_code=HTTPStatus.OK, content=result)

# ✅ yfinance stock info
def get_live_stock_info(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or "currentPrice" not in info:
            raise ValueError("Stock data not available")

        return {
            "ticker": ticker,
            "name": safe_value(info.get("longName", "N/A")),
            "price": safe_value(info.get("currentPrice", "N/A")),
            "open": safe_value(info.get("open", "N/A")),
            "high": safe_value(info.get("dayHigh", "N/A")),
            "low": safe_value(info.get("dayLow", "N/A")),
            "volume": safe_value(info.get("volume", "N/A")),
            "link": f"https://finance.yahoo.com/quote/{ticker}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Error fetching stock info: {str(e)}"
        )

# ✅ /stock/{ticker} endpoint
@app.get("/stock/{ticker}", status_code=HTTPStatus.OK)
async def get_one_stock(ticker: str):
    return await run_in_threadpool(lambda: get_live_stock_info(ticker))
class StockRequest(BaseModel):
    tickers: List[str]
# ✅ ML results stub
@app.post("/stocks/ml-results", status_code=HTTPStatus.OK)
def get_batch_stocks(request: StockRequest):
    print(request)
    result = [
        {"ticker": "AAPL", "name": "Apple Inc.", "score": 0.96},
        {"ticker": "MSFT", "name": "Microsoft Corporation", "score": 0.94},
        {"ticker": "GOOGL", "name": "Alphabet Inc.", "score": 0.91}
    ]
    return  result
