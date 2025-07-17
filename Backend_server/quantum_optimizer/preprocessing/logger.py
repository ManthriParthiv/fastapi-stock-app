import time, threading


class APILogger:
    def __init__(self):
        self.lock = threading.Lock()
        self.calls = []

    def log_call(self, name: str, duration: float):
        """Register one API call name and its duration (s)."""
        with self.lock:
            self.calls.append((name, duration))

    def summary(self):
        """Return count + 10/25/50/75/100-percentile timings."""
        times = sorted(d for _, d in self.calls)

        def pct(p):
            idx = min(len(times) - 1, int(len(times) * p / 100))
            return times[idx]

        return {
            "count": len(times),
            "10%": pct(10),
            "25%": pct(25),
            "50%": pct(50),
            "75%": pct(75),
            "100%": pct(100),
        }


api_logger = APILogger()
