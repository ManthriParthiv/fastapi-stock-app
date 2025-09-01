# quantum_optimizer/preprocessing/fetch_fundamentals.py
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from .logger import api_logger

# Parameters we need for quantum optimization
ESSENTIAL_PARAMS = {
    'PE': 'trailingPE',
    'PB': 'priceToBook',
    'ROE': 'returnOnEquity',
    'EV/EBITDA': 'enterpriseToEbitda',
    'RevenueGrowth': 'revenueGrowth',
    'PEGRatio': 'pegRatio',
    'NetMargin': 'profitMargins',
    'FreeCF': 'freeCashflow',
    'OpMargin': 'operatingMargins',
    'P/S': 'priceToSalesTrailing12Months',
    'Payout': 'payoutRatio',
    'CurrRatio': 'currentRatio'
}

def fetch_single_ticker(ticker: str) -> dict:
    """Fetch fundamentals for a single ticker with error handling"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        data = {"Ticker": ticker}
        for param, yf_key in ESSENTIAL_PARAMS.items():
            data[param] = info.get(yf_key)
        
        data['LastUpdated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return data
        
    except Exception as e:
        # Use the correct logger method based on what's available
        if hasattr(api_logger, 'log'):
            api_logger.log(f"Failed {ticker}: {str(e)}", level='ERROR')
        elif hasattr(api_logger, 'log_call'):
            api_logger.log_call(f"Error:{ticker}", 0)
        else:
            print(f"ERROR: Failed {ticker}: {str(e)}")
        return None

def fetch_fundamentals(tickers: list, outpath: str, max_workers: int = 5) -> pd.DataFrame:
    """
    Fetch fundamentals for multiple tickers with parallel processing
    """
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ticker = {
            executor.submit(fetch_single_ticker, ticker): ticker 
            for ticker in tickers
        }
        
        for future in future_to_ticker:
            result = future.result()
            if result:
                results.append(result)
    
    if results:
        df = pd.DataFrame(results).set_index("Ticker")
        df.to_csv(outpath)
        
        # Use the correct logging method
        if hasattr(api_logger, 'log'):
            api_logger.log(f"Saved fundamentals for {len(df)} tickers to {outpath}")
        elif hasattr(api_logger, 'log_call'):
            api_logger.log_call("FundamentalsSaved", len(df))
        else:
            print(f"INFO: Saved fundamentals for {len(df)} tickers")
        
        return df
    else:
        if hasattr(api_logger, 'log'):
            api_logger.log("No fundamentals data was fetched", level='WARNING')
        else:
            print("WARNING: No fundamentals data was fetched")
        return pd.DataFrame()

if __name__ == "__main__":
    # Test with sample tickers
    test_tickers = ["TCS.NS", "SIEMENS.NS", "NHPC.NS", "IDEA.NS"]
    fetch_fundamentals(test_tickers, "./data/fundamentals.csv")