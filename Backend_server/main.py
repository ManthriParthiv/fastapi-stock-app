from fastapi import FastAPI, Query
from fastapi.concurrency import run_in_threadpool
import yfinance as yf
import pandas as pd
import math
from tickers import tickers  # Assuming you have a module to load tickers
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app = FastAPI()

# ✅ Allow CORS for your frontend (like Vite on port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # <-- frontend origin
    allow_credentials=True,
    allow_methods=["*"],                      # <-- allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],                      # <-- allow all headers
)

# ✅ Load tickers and names from CSV
df, tickers = tickers()

def safe_value(val):
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None
    return val

@app.get("/")
def home():
    return {"message": "📈 FastAPI Stock API — CSV list + Live details"}

#  Lightweight CSV-based paginated stock list
@app.get("/stocks")
def get_stocks(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500)
):
    start = (page - 1) * limit
    end = start + limit
    selected_rows = df.iloc[start:end]

    def clean(val):
        if pd.isna(val) or val in [float("inf"), float("-inf")]:
            return None
        return val

    result = [
        {
            "ticker": clean(row["Symbol"]),
            "name": clean(row["Name"]),
        }
        for _, row in selected_rows.iterrows()
    ]
    return result

#  Live /stock/{ticker} using yfinance
def get_live_stock_info(ticker: str):
    print(ticker)
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        stockData={     "ticker": ticker,
            "name": safe_value(info.get("longName", "N/A")),
            "price": safe_value(info.get("currentPrice", "N/A")),
            "open": safe_value(info.get("open", "N/A")),
            "high": safe_value(info.get("dayHigh", "N/A")),
            "low": safe_value(info.get("dayLow", "N/A")),
            "volume": safe_value(info.get("volume", "N/A")),
            "link": f"https://finance.yahoo.com/quote/{ticker}"
        }
        return stockData
    except Exception as e:
        return {
            "ticker": ticker,
            "error": str(e),
            "link": f"https://finance.yahoo.com/quote/{ticker}"
        }

@app.get("/stock/{ticker}")
async def get_one_stock(ticker: str):
    return await run_in_threadpool(lambda: get_live_stock_info(ticker))
@app.post("/Stocks/ml-results")
def get_batch_stocks():
 result=[
  { "ticker": "AAPL", "name": "Apple Inc.", "score": 0.96 },
  { "ticker": "MSFT", "name": "Microsoft Corporation", "score": 0.94 },
  { "ticker": "GOOGL", "name": "Alphabet Inc.", "score": 0.91 }
]

 return result