# quantum_optimizer/preprocessing/fetch_data.py
import yfinance as yf
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor
from .logger import api_logger

def fetch_single_ticker(ticker: str, period: str = "6mo") -> pd.Series:
    """Fetch price data for a single ticker with robust error handling"""
    try:
        start = time.time()
        # Explicitly set auto_adjust to silence warning
        df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
        dur = time.time() - start
        api_logger.log_call(f"yfinance.download.{ticker}", dur)
        
        # Handle both single and multi-column cases
        if 'Close' in df.columns:
            series = df['Close']
        elif 'Adj Close' in df.columns:
            series = df['Adj Close']
        else:
            raise ValueError("No Close/Adj Close column found")
        
        # Proper series naming without using rename()
        series.name = ticker
        return series
            
    except Exception as e:
        # Use the correct logger method
        if hasattr(api_logger, 'log'):
            api_logger.log(f"Failed {ticker}: {str(e)}", level='ERROR')
        else:
            print(f"ERROR: Failed {ticker}: {str(e)}")  # Fallback
        return pd.Series(dtype='float64', name=ticker)

def fetch_and_cache(tickers: list, outpath: str, period: str = "6mo", max_workers: int = 3) -> pd.DataFrame:
    """
    Enhanced version with:
    - Proper series naming
    - More robust error handling
    """
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ticker = {
            executor.submit(fetch_single_ticker, ticker, period): ticker
            for ticker in tickers
        }
        
        for future in future_to_ticker:
            try:
                result = future.result()
                if not result.empty:
                    results.append(result)
            except Exception as e:
                if hasattr(api_logger, 'log'):
                    api_logger.log(f"Processing failed: {str(e)}", level='ERROR')
                else:
                    print(f"ERROR: Processing failed: {str(e)}")
    
    if results:
        df = pd.concat(results, axis=1)
        df.to_csv(outpath)
        if hasattr(api_logger, 'log'):
            api_logger.log(f"Saved price data for {len(df.columns)} tickers to {outpath}")
        return df
    else:
        if hasattr(api_logger, 'log'):
            api_logger.log("No price data was fetched", level='WARNING')
        return pd.DataFrame()

if __name__ == "__main__":
    tickers = ["TCS.NS", "SIEMENS.NS", "NHPC.NS", "IDEA.NS"]
    df = fetch_and_cache(tickers, "./data/last6m.csv")
    print("API call stats:", api_logger.summary())