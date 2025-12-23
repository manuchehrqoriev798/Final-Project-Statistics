"""
Statistical Analysis Module
Performs probability calculations and statistical analysis
"""

import pandas as pd
import numpy as np
from scipy import stats


def calculate_bernoulli_parameters(df, infection_col="I", vaccination_col="vaccination_rate"):
    """
    Calculate Bernoulli parameters for infection and vaccination
    
    Args:
        df: DataFrame with infection and vaccination data
        infection_col: Column name for infection indicator
        vaccination_col: Column name for vaccination rate
    
    Returns:
        Dictionary with calculated parameters
    """
    p_I = df[infection_col].mean()
    p_V = df[vaccination_col].mean()
    
    var_I = p_I * (1 - p_I)
    var_V = p_V * (1 - p_V)
    
    results = {
        "p_I": p_I,
        "p_V": p_V,
        "var_I": var_I,
        "var_V": var_V,
        "std_I": np.sqrt(var_I),
        "std_V": np.sqrt(var_V)
    }
    
    return results


def calculate_conditional_probabilities(df, infection_col="I", vaccination_col="vaccination_rate", threshold=0.5):
    """
    Calculate conditional infection probabilities for high vs low vaccination
    
    Args:
        df: DataFrame with infection and vaccination data
        infection_col: Column name for infection indicator
        vaccination_col: Column name for vaccination rate
        threshold: Vaccination rate threshold (default: 0.5)
    
    Returns:
        Dictionary with conditional probabilities
    """
    high_vax = df[df[vaccination_col] >= threshold]
    low_vax = df[df[vaccination_col] < threshold]
    
    p_I_high = high_vax[infection_col].mean()
    p_I_low = low_vax[infection_col].mean()
    
    # Calculate sample sizes
    n_high = len(high_vax)
    n_low = len(low_vax)
    
    # Calculate confidence intervals (approximate)
    se_high = np.sqrt(p_I_high * (1 - p_I_high) / n_high) if n_high > 0 else 0
    se_low = np.sqrt(p_I_low * (1 - p_I_low) / n_low) if n_low > 0 else 0
    
    results = {
        "p_I_high": p_I_high,
        "p_I_low": p_I_low,
        "difference": p_I_high - p_I_low,
        "n_high": n_high,
        "n_low": n_low,
        "se_high": se_high,
        "se_low": se_low,
        "threshold": threshold
    }
    
    return results


def calculate_binomial_parameters(df, period="W", infection_col="I"):
    """
    Calculate Binomial distribution parameters for weekly/monthly infections
    
    Args:
        df: DataFrame with datetime index and infection data
        period: Period for aggregation ('W' for weekly, 'M' for monthly)
        infection_col: Column name for infection indicator
    
    Returns:
        Dictionary with Binomial parameters and comparison
    """
    # Calculate daily infection probability
    p_I = df[infection_col].mean()
    
    # Determine number of trials based on period
    if period == "W":
        n_trials = 7
    elif period == "M" or period == "ME":
        n_trials = 30  # Approximate
    else:
        n_trials = 7
    
    # Expected value and variance for Binomial(n, p)
    E_period = n_trials * p_I
    Var_period = n_trials * p_I * (1 - p_I)
    
    # Aggregate actual data
    if period == "W":
        actual = df[infection_col].resample("W").sum()
    elif period == "M" or period == "ME":
        actual = df[infection_col].resample("ME").sum()
    else:
        actual = df[infection_col].resample(period).sum()
    
    actual_mean = actual.mean()
    actual_var = actual.var()
    
    results = {
        "period": period,
        "n_trials": n_trials,
        "p_I": p_I,
        "expected_mean": E_period,
        "expected_variance": Var_period,
        "actual_mean": actual_mean,
        "actual_variance": actual_var,
        "mean_difference": actual_mean - E_period,
        "variance_difference": actual_var - Var_period
    }
    
    return results, actual


def perform_statistical_tests(df, infection_col="I", vaccination_col="vaccination_rate", threshold=0.5):
    """
    Perform statistical tests to compare high vs low vaccination groups
    
    Args:
        df: DataFrame with infection and vaccination data
        infection_col: Column name for infection indicator
        vaccination_col: Column name for vaccination rate
        threshold: Vaccination rate threshold
    
    Returns:
        Dictionary with test results
    """
    high_vax = df[df[vaccination_col] >= threshold][infection_col]
    low_vax = df[df[vaccination_col] < threshold][infection_col]
    
    # Two-sample proportion test (z-test)
    n1, n2 = len(high_vax), len(low_vax)
    x1, x2 = high_vax.sum(), low_vax.sum()
    p1, p2 = x1 / n1 if n1 > 0 else 0, x2 / n2 if n2 > 0 else 0
    
    # Pooled proportion
    p_pooled = (x1 + x2) / (n1 + n2) if (n1 + n2) > 0 else 0
    
    # Standard error
    se = np.sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2)) if (n1 + n2) > 0 else 0
    
    # Z-statistic
    z_stat = (p1 - p2) / se if se > 0 else 0
    
    # P-value (two-tailed)
    p_value = 2 * (1 - stats.norm.cdf(abs(z_stat))) if se > 0 else 1.0
    
    results = {
        "test_type": "Two-sample proportion test (z-test)",
        "n_high": n1,
        "n_low": n2,
        "p_high": p1,
        "p_low": p2,
        "difference": p1 - p2,
        "z_statistic": z_stat,
        "p_value": p_value,
        "significant": p_value < 0.05
    }
    
    return results


def run_complete_analysis(df, infection_col="I", vaccination_col="vaccination_rate"):
    """
    Run complete statistical analysis
    
    Args:
        df: Processed DataFrame with infection and vaccination data
        infection_col: Column name for infection indicator
        vaccination_col: Column name for vaccination rate
    
    Returns:
        Dictionary with all analysis results
    """
    print("=" * 60)
    print("STATISTICAL ANALYSIS")
    print("=" * 60)
    
    # Bernoulli parameters
    print("\n1. Calculating Bernoulli parameters...")
    bernoulli = calculate_bernoulli_parameters(df, infection_col, vaccination_col)
    print(f"   p_I (infection probability): {bernoulli['p_I']:.4f}")
    print(f"   p_V (vaccination rate): {bernoulli['p_V']:.4f}")
    print(f"   Var(I): {bernoulli['var_I']:.4f}")
    print(f"   Var(V): {bernoulli['var_V']:.4f}")
    
    # Conditional probabilities
    print("\n2. Calculating conditional probabilities...")
    conditional = calculate_conditional_probabilities(df, infection_col, vaccination_col)
    print(f"   P(I=1 | V >= 0.5): {conditional['p_I_high']:.4f}")
    print(f"   P(I=1 | V < 0.5): {conditional['p_I_low']:.4f}")
    print(f"   Difference: {conditional['difference']:.4f}")
    
    # Binomial parameters (weekly)
    print("\n3. Calculating Binomial parameters (weekly)...")
    binomial_weekly, weekly_actual = calculate_binomial_parameters(df, period="W", infection_col=infection_col)
    print(f"   Expected weekly infections: {binomial_weekly['expected_mean']:.3f}")
    print(f"   Actual weekly average: {binomial_weekly['actual_mean']:.3f}")
    print(f"   Expected variance: {binomial_weekly['expected_variance']:.3f}")
    print(f"   Actual variance: {binomial_weekly['actual_variance']:.3f}")
    
    # Statistical tests
    print("\n4. Performing statistical tests...")
    test_results = perform_statistical_tests(df, infection_col, vaccination_col)
    print(f"   Z-statistic: {test_results['z_statistic']:.4f}")
    print(f"   P-value: {test_results['p_value']:.4f}")
    print(f"   Significant: {test_results['significant']}")
    
    # Compile all results
    all_results = {
        "bernoulli": bernoulli,
        "conditional": conditional,
        "binomial_weekly": binomial_weekly,
        "statistical_tests": test_results,
        "weekly_actual": weekly_actual
    }
    
    return all_results


if __name__ == "__main__":
    print("Statistical analysis module loaded successfully!")

