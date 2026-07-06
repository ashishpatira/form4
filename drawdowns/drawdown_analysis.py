import numpy as np
import pandas as pd

def simulate_timeseries(days=5000, initial_price=100.0, drift=0.1, annualized_volatility=0.20):
    """
    Simulates a daily timeseries for a given number of days.

    Formula: Price[t] = Price[t-1] * (1 + annual_drift/252 + random_normal(mean=0, std=annualized_volatility/sqrt(252)))
    """
    np.random.seed(42)  # For reproducibility

    daily_vol = annualized_volatility / np.sqrt(252)

    # Generate random noise for the whole timeseries at once
    noise = np.random.normal(0, daily_vol, days)

    # Vectorized optimization: calculate multipliers and apply cumprod
    multipliers = drift/252 + 1 + noise

    # Identify the first boundary breach (multiplier <= 0) and zero out subsequent multipliers
    # to emulate an absorbing barrier at 0 without mathematical regression.
    is_negative = multipliers <= 0
    if np.any(is_negative):
        first_zero_idx = np.argmax(is_negative)
        multipliers[first_zero_idx:] = 0

    prices = np.empty(days + 1)
    prices[0] = initial_price
    prices[1:] = initial_price * np.cumprod(multipliers)

    return prices

def calculate_drawdowns(prices):
    """
    Calculates the all-time high (ATH) and percentage drawdown for each daily price.
    Drawdown = (ATH - Price) / ATH * 100
    Returns drawdowns rounded to 1 decimal place.
    """
    df = pd.DataFrame({'price': prices})
    df['ath'] = df['price'].cummax()

    # Calculate percentage drawdown: (ATH - Price) / ATH * 100
    # Use np.where to avoid division by zero just in case ATH is 0 (though initial is 100)
    df['drawdown_pct'] = np.where(df['ath'] > 0,
                                  (df['ath'] - df['price']) / df['ath'] * 100,
                                  0.0)

    # Round to 1 decimal place
    df['rounded_drawdown'] = df['drawdown_pct'].round(1)

    return df


def analyze_drawdown_probabilities(df):
    """
    Calculates the probability that a specific drawdown level is the lowest
    before the price never returns to that level again (or lower) for the remainder
    of the timeseries.

    A drawdown level D% is "successful" if for all remaining days, the drawdown
    is strictly less than D%.
    """
    # Note: we work with the rounded drawdown
    # We want to know for each day 't', does any future day have a drawdown >= this day's drawdown?
    # Equivalent to: is the MAXIMUM future drawdown < this day's drawdown?

    # Calculate the rolling maximum of future drawdowns
    # We flip the array, take cummax, and flip back
    # Need to shift by 1 to get *strictly future* maximums
    future_max_drawdowns = df['rounded_drawdown'].iloc[::-1].cummax().iloc[::-1]
    df['future_max_drawdown'] = future_max_drawdowns.shift(-1)

    # For the last day, there are no future days, so we can't really judge its "future".
    # We'll drop the last day or consider it unsuccessful.
    df['future_max_drawdown'] = df['future_max_drawdown'].fillna(0.0)

    # Determine if it's a success
    # Success condition: all future drawdowns are <= this day's drawdown.
    # Note from user: "for all future days in the timeseries, the drawdown is less than or equal to D%"
    # So if future_max_drawdown <= D%, it's a success.
    df['success'] = df['future_max_drawdown'] <= df['rounded_drawdown']

    # We should exclude the last day since it has no future to measure against,
    # but practically we can keep it as part of the total if we just treat it as True or False,
    # however dropping it is usually statistically safer for a "future" predictive check.
    # Let's keep it for now but note it's just 1 day out of 5000.

    # Calculate probabilities
    # Group by the rounded drawdown value
    results = df.groupby('rounded_drawdown').agg(
        occurrences=('success', 'count'),
        successes=('success', 'sum')
    ).reset_index()

    results['probability_pct'] = (results['successes'] / results['occurrences']) * 100.0

    # Sort by drawdown value for presentation
    results = results.sort_values('rounded_drawdown')

    return results

if __name__ == "__main__":
    import argparse
    from tabulate import tabulate

    parser = argparse.ArgumentParser(description="Simulate a timeseries and analyze drawdown probabilities.")
    parser.add_argument("--days", type=int, default=5000, help="Number of days to simulate (default: 5000).")
    parser.add_argument("--initial-price", type=float, default=100.0, help="Initial price on day 0 (default: 100.0).")
    parser.add_argument("--drift", type=float, default=0.1, help="Average Annual drift (default: 0.1).")
    parser.add_argument("--volatility", type=float, default=0.20, help="Annualized volatility (default: 0.20).")

    args = parser.parse_args()

    print(f"Running simulation with {args.days} days, initial price ${args.initial_price}, drift ${args.drift}, and {args.volatility*100}% volatility...")

    prices = simulate_timeseries(
        days=args.days,
        initial_price=args.initial_price,
        drift=args.drift,
        annualized_volatility=args.volatility
    )

    df = calculate_drawdowns(prices)
    results = analyze_drawdown_probabilities(df)

    print(tabulate(results, headers='keys', tablefmt='psql', showindex=False))
