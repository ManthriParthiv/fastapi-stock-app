import numpy as np
from tabulate import tabulate
import yfinance as yf
import time
from preprocessing.logger import api_logger

def compile_results(
    tickers,
    weights: np.ndarray,
    mu: np.ndarray,
    cov: np.ndarray,
    risk_free_rate: float = 0.05,
):
    """
    1) Compute portfolio return, risk, Sharpe ratio
    2) Fetch each stock’s fundamentals (once)
    3) Log API timings
    4) Print two tables of 8 params each
    5) Print number of params + portfolio metrics
    """
    # 1) Portfolio metrics
    ret    = float(np.dot(weights, mu))
    risk   = float(np.sqrt(weights @ cov @ weights.T))
    sharpe = (ret - risk_free_rate) / risk

    # 2) All 16 fields in order
    all_fields = [
        ("trailingPE",                   "P/E"),
        ("priceToBook",                  "P/B"),
        ("returnOnEquity",               "ROE"),
        ("currentPrice",                 "Curr"),
        ("debtToEquity",                 "D/E"),
        ("enterpriseToEbitda",           "EV/EBITDA"),
        ("beta",                         "Beta"),
        ("marketCap",                    "MktCap"),
        ("revenueGrowth",                "RevGrowth"),
        ("pegRatio",                     "PEG"),
        ("profitMargins",                "NetMargin"),
        ("freeCashflow",                 "FreeCF"),
        ("operatingMargins",             "OpMargin"),
        ("priceToSalesTrailing12Months", "P/S"),
        ("payoutRatio",                  "Payout"),
        ("currentRatio",                 "CurrRatio"),
    ]

    # split into two halves of 8 each
    left_fields  = all_fields[:8]
    right_fields = all_fields[8:]

    # 3) Fetch fundamentals once per ticker
    rows = []
    for tkr, w in zip(tickers, weights):
        start = time.time()
        info  = yf.Ticker(tkr).info
        api_logger.log_call("yfinance.Ticker.info", time.time() - start)

        # build a single “flat” row of 2 + 16 entries
        row = [tkr, f"{w:.2%}"]
        for raw, _ in all_fields:
            val = info.get(raw, None)
            if isinstance(val, (int, float, np.integer, np.floating)):
                row.append(f"{val:.4f}")
            else:
                row.append(val if val else "-")
        rows.append(row)

    # 4) Print API timing
    print("\nAPI timing summary:", api_logger.summary(), "\n")

    # 5) Prepare and print the **left** table
    left_headers  = ["Ticker", "Weight"] + [lbl for _, lbl in left_fields]
    left_table    = [
        row[:2 + len(left_fields)]
        for row in rows
    ]
    print("— Portfolio Fundamentals (1/2) —\n")
    print(tabulate(
        left_table,
        headers=left_headers,
        tablefmt="github",
        numalign="right",
        stralign="center",
    ))
    print()

    # 6) Prepare and print the **right** table
    right_headers = ["Ticker", "Weight"] + [lbl for _, lbl in right_fields]
    right_table   = [
        # skip first two entries, take next 8
        [r[0], r[1]] + r[2 + len(left_fields):]
        for r in rows
    ]
    print("— Portfolio Fundamentals (2/2) —\n")
    print(tabulate(
        right_table,
        headers=right_headers,
        tablefmt="github",
        numalign="right",
        stralign="center",
    ))
    print()

    # 7) Footer: count + metrics
    print(f"Displayed {len(all_fields)} fundamental parameters ({len(left_fields)} + {len(right_fields)}).\n")
    print(f"Portfolio → Return: {ret:.2%}, Risk: {risk:.2%}, Sharpe: {sharpe:.2f}\n")








































#messed table with 16 params
# import numpy as np
# import time
# from tabulate import tabulate
# import yfinance as yf
# from preprocessing.logger import api_logger


# def compile_results(tickers, weights, mu, cov, risk_free_rate=0.05):
#     """
#     1) Compute portfolio return, risk, and Sharpe ratio
#     2) Fetch each stock’s fundamentals
#     3) Log API call timings
#     4) Print a neat table + metrics
#     """
#     # 1) portfolio metrics
#     ret = np.dot(weights, mu)
#     risk = np.sqrt(weights @ cov @ weights.T)
#     sharpe = (ret - risk_free_rate) / risk

#     # 2) fetch fundamentals and build table rows
#     rows = []
#     for t, w in zip(tickers, weights):
#         start = time.time()
#         info = yf.Ticker(t).info
#         dur = time.time() - start
#         api_logger.log_call("yfinance.Ticker.info", dur)

#         rows.append(
#             [
#                 t,
#                 f"{w:.2%}",
#                 info.get("trailingPE", "-"),
#                 info.get("priceToBook", "-"),
#                 info.get("returnOnEquity", "-"),
#                 info.get("currentPrice", "-"),
#                 info.get("debtToEquity", "-"),
#                 info.get("enterpriseToEbitda","-"),
#                 info.get("beta","-"),
#                 info.get("marketCap","-"),
#                 info.get("revenueGrowth","-"),
#                 info.get("pegRatio","-"),
#                 info.get("profitMargins","-"),
#                 info.get("freeCashflow","-"),
#                 info.get("operatingMargins","-"),
#                 info.get("priceToSalesTrailing12Months","-"),
#                 info.get("payoutRatio","-"),
#                 info.get("currentRatio","-"),
#             ]
#         )

#     # 3) print API timing summary
#     print("API timing summary:", api_logger.summary())

#     # 4) print table
#     print(
#         tabulate(
#             rows,
#             headers=["Tkr", "Weight", "P/E", "P/B", "ROE", "Curr", "D/E","EV/EBITDA","Beta","MktCap", "RevGrowth","PEG","NetMargin","FreeCF","OpMargin","P/S","Payout","CurrRatio"],
#             tablefmt="github",
#         )
#     )

#     # 5) print portfolio metrics
#     print(f"\nPortfolio → Return: {ret:.2%}, Risk: {risk:.2%}, Sharpe: {sharpe:.2f}")
