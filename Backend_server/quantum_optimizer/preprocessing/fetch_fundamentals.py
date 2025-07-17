# preprocessing/fetch_fundamentals.py
import time
import yfinance as yf
import pandas as pd
from .logger import api_logger


def fetch_fundamentals(tickers, outpath):
    rows = []
    for t in tickers:
        start = time.time()
        info = yf.Ticker(t).info
        dur = time.time() - start
        api_logger.log_call("yfinance.Ticker.info", dur)
        rows.append(
            {
                "Ticker": t,
                "PE": info.get("trailingPE", None),
                "PB": info.get("priceToBook", None),
                "ROE": info.get("returnOnEquity", None),
                "Volume": info.get("volume", None),
                "EarningsDate": ";".join(map(str, info.get("earningsDate", []))),
                "EV/EBITDA":     info.get("enterpriseToEbitda",   None),
                "Beta":          info.get("beta",                 None),
                "MarketCap":     info.get("marketCap",            None),
                "RevenueGrowth": info.get("revenueGrowth",       None),
                "PEGRatio":      info.get("pegRatio",            None),
                "NetMargin":     info.get("profitMargins",       None),
                "FreeCF":        info.get("freeCashflow",                 None),
                "OpMargin":      info.get("operatingMargins",             None),
                "P/S":           info.get("priceToSalesTrailing12Months", None),
                "Payout":        info.get("payoutRatio",                  None),
                "CurrRatio":     info.get("currentRatio",                 None),
            }
        )
    df = pd.DataFrame(rows).set_index("Ticker")
    df.to_csv(outpath)
    return df
