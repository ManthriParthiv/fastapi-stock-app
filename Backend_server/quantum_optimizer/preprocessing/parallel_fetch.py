import concurrent.futures
from .fetch_data import fetch_and_cache


def parallel_fetch(ticker_groups, outpaths, period="6mo", max_workers=4):
    """
    Run fetch_and_cache() on each ticker group in parallel.
    """
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as exe:
        futures = {
            exe.submit(fetch_and_cache, grp, path, period): (grp, path)
            for grp, path in zip(ticker_groups, outpaths)
        }
        for fut in concurrent.futures.as_completed(futures):
            grp, path = futures[fut]
            try:
                df = fut.result()
                results[path] = df
            except Exception as e:
                print(f"Error fetching {grp!r}: {e}")
    return results
