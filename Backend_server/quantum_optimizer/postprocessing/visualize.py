import matplotlib.pyplot as plt


def plot_weights(tickers, weights):
    """
    Bar‐plot of optimal allocations.
    Green bars = above‐average weight, red = below.
    """
    avg = weights.mean()
    colors = ["green" if w >= avg else "red" for w in weights]

    plt.figure(figsize=(8, 4))
    plt.bar(tickers, weights, color=colors)
    plt.title("Optimal Portfolio Weights")
    plt.ylabel("Weight")
    plt.axhline(avg, color="gray", linestyle="--", label="Average")
    plt.legend()
    plt.tight_layout()
    plt.show()
