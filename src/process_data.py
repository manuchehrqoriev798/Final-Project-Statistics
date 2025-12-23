"""
Data Processing Module
Cleans, processes, and aggregates COVID-19 data
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime


def filter_country_data(owid_df, who_df, country="United States"):
    """
    Filter data for a specific country
    
    Args:
        owid_df: OWID DataFrame
        who_df: WHO DataFrame
        country: Country name to filter
    
    Returns:
        Tuple of filtered DataFrames
    """
    # OWID uses "United States", WHO uses "United States of America"
    country_mapping = {
        "United States": ("United States", "United States of America"),
        "USA": ("United States", "United States of America"),
    }
    
    if country in country_mapping:
        owid_name, who_name = country_mapping[country]
    else:
        owid_name = country
        who_name = country
    
    # Filter OWID data
    owid_filtered = owid_df[owid_df["location"] == owid_name].copy()
    
    # Filter WHO data
    who_filtered = who_df[who_df["Country"] == who_name].copy()
    
    print(f"Filtered data for {country}:")
    print(f"  OWID: {len(owid_filtered)} rows")
    print(f"  WHO: {len(who_filtered)} rows")
    
    return owid_filtered, who_filtered


def clean_owid_data(df):
    """
    Clean and process OWID data
    
    Args:
        df: OWID DataFrame
    
    Returns:
        Cleaned DataFrame
    """
    df = df.copy()
    
    # Convert date to datetime
    df["date"] = pd.to_datetime(df["date"])
    
    # Forward fill vaccination data (carry forward last known value)
    df["people_vaccinated"] = df["people_vaccinated"].ffill()
    
    # Fill missing new_cases with 0
    df["new_cases"] = df["new_cases"].fillna(0)
    
    # Compute vaccination rate
    if "population" in df.columns and "people_vaccinated" in df.columns:
        df["vaccination_rate"] = df["people_vaccinated"] / df["population"]
        df["vaccination_rate"] = df["vaccination_rate"].fillna(0)
    
    # Define binary infection variable
    df["I"] = (df["new_cases"] > 0).astype(int)
    
    # Set date as index for easier resampling
    df = df.set_index("date")
    
    return df


def clean_who_data(df):
    """
    Clean and process WHO data
    
    Args:
        df: WHO DataFrame
    
    Returns:
        Cleaned DataFrame
    """
    df = df.copy()
    
    # Rename columns for consistency
    df = df.rename(columns={
        "Date_reported": "date",
        "New_cases": "new_cases"
    })
    
    # Convert date to datetime
    df["date"] = pd.to_datetime(df["date"])
    
    # Define binary infection variable
    df["I"] = (df["new_cases"] > 0).astype(int)
    
    # Set date as index
    df = df.set_index("date")
    
    return df


def aggregate_by_period(df, period="W", column="I"):
    """
    Aggregate data by time period (daily, weekly, monthly)
    Includes all relevant columns for comprehensive analysis
    
    Args:
        df: DataFrame with datetime index
        period: Period for aggregation ('D', 'W', 'ME' for monthly)
        column: Primary column to aggregate
    
    Returns:
        Aggregated DataFrame with all relevant metrics
    """
    # Select columns to aggregate
    cols_to_agg = {}
    
    # Always include the primary column
    if column in df.columns:
        cols_to_agg[column] = ["sum", "mean", "count"]
    
    # Include vaccination rate if available
    if "vaccination_rate" in df.columns:
        cols_to_agg["vaccination_rate"] = ["mean", "max", "min"]
    
    # Include new cases if available
    if "new_cases" in df.columns:
        cols_to_agg["new_cases"] = ["sum", "mean", "max"]
    
    # Include people vaccinated if available
    if "people_vaccinated" in df.columns:
        cols_to_agg["people_vaccinated"] = ["mean", "max"]
    
    if period == "D":
        return df.copy()
    elif period == "W":
        if not cols_to_agg:
            return pd.DataFrame({'date': df.index}).set_index('date')
        aggregated = df[list(cols_to_agg.keys())].resample("W").agg(cols_to_agg)
        aggregated = aggregated.reset_index()
        # Flatten column names properly
        new_cols = []
        for col in aggregated.columns:
            if isinstance(col, tuple):
                if col[1]:
                    new_cols.append(f"{col[0]}_{col[1]}")
                else:
                    new_cols.append(col[0])
            else:
                new_cols.append(col)
        aggregated.columns = new_cols
        return aggregated
    elif period == "M" or period == "ME":
        if not cols_to_agg:
            return pd.DataFrame({'date': df.index}).set_index('date')
        aggregated = df[list(cols_to_agg.keys())].resample("ME").agg(cols_to_agg)
        aggregated = aggregated.reset_index()
        # Flatten column names properly
        new_cols = []
        for col in aggregated.columns:
            if isinstance(col, tuple):
                if col[1]:
                    new_cols.append(f"{col[0]}_{col[1]}")
                else:
                    new_cols.append(col[0])
            else:
                new_cols.append(col)
        aggregated.columns = new_cols
        return aggregated
    else:
        if not cols_to_agg:
            return pd.DataFrame({'date': df.index}).set_index('date')
        aggregated = df[list(cols_to_agg.keys())].resample(period).agg(cols_to_agg)
        aggregated = aggregated.reset_index()
        new_cols = []
        for col in aggregated.columns:
            if isinstance(col, tuple):
                if col[1]:
                    new_cols.append(f"{col[0]}_{col[1]}")
                else:
                    new_cols.append(col[0])
            else:
                new_cols.append(col)
        aggregated.columns = new_cols
        return aggregated


def merge_datasets(owid_df, who_df):
    """
    Merge OWID and WHO datasets
    
    Args:
        owid_df: Cleaned OWID DataFrame
        who_df: Cleaned WHO DataFrame
    
    Returns:
        Merged DataFrame
    """
    # Reset index to make date a column for merging
    owid_reset = owid_df[["vaccination_rate", "I", "new_cases", "people_vaccinated"]].reset_index()
    who_reset = who_df[["new_cases", "I"]].reset_index()
    
    # Merge on date
    merged = pd.merge(
        owid_reset,
        who_reset[["date", "I"]],
        on="date",
        how="inner",
        suffixes=("_owid", "_who")
    )
    
    # Create combined I column (use OWID I as primary, fallback to WHO I)
    if "I_owid" in merged.columns:
        merged["I"] = merged["I_owid"]
    elif "I_who" in merged.columns:
        merged["I"] = merged["I_who"]
    else:
        # If neither exists, create from new_cases
        merged["I"] = (merged.get("new_cases_owid", merged.get("new_cases", 0)) > 0).astype(int)
    
    # Set date as index again
    merged = merged.set_index("date")
    
    print(f"Merged dataset: {len(merged)} rows")
    
    return merged


def process_all_data(owid_df, who_df, country="United States", save_processed=True):
    """
    Complete data processing pipeline
    
    Args:
        owid_df: Raw OWID DataFrame
        who_df: Raw WHO DataFrame
        country: Country to process
        save_processed: Whether to save processed data
    
    Returns:
        Tuple of (processed_owid, processed_who, merged_df)
    """
    print("=" * 60)
    print("DATA PROCESSING")
    print("=" * 60)
    
    # Filter by country
    owid_filtered, who_filtered = filter_country_data(owid_df, who_df, country)
    
    # Clean data
    print("\nCleaning OWID data...")
    owid_cleaned = clean_owid_data(owid_filtered)
    
    print("Cleaning WHO data...")
    who_cleaned = clean_who_data(who_filtered)
    
    # Merge datasets
    print("\nMerging datasets...")
    merged_df = merge_datasets(owid_cleaned, who_cleaned)
    
    # Save processed data
    if save_processed:
        os.makedirs("data/processed", exist_ok=True)
        
        owid_cleaned.reset_index().to_csv(
            "data/processed/owid_processed.csv", index=False
        )
        who_cleaned.reset_index().to_csv(
            "data/processed/who_processed.csv", index=False
        )
        merged_df.reset_index().to_csv(
            "data/processed/merged_data.csv", index=False
        )
        
        print("\nProcessed data saved to data/processed/")
    
    # Create aggregated datasets
    print("\nCreating aggregated datasets...")
    
    # Weekly aggregation
    weekly_owid = aggregate_by_period(owid_cleaned, period="W", column="I")
    weekly_who = aggregate_by_period(who_cleaned, period="W", column="I")
    
    # Monthly aggregation
    monthly_owid = aggregate_by_period(owid_cleaned, period="ME", column="I")
    monthly_who = aggregate_by_period(who_cleaned, period="ME", column="I")
    
    # Add country information to aggregated datasets
    if save_processed:
        weekly_owid.insert(0, "country", country)
        weekly_who.insert(0, "country", country)
        monthly_owid.insert(0, "country", country)
        monthly_who.insert(0, "country", country)
        
        weekly_owid.to_csv("data/processed/owid_weekly.csv", index=False)
        weekly_who.to_csv("data/processed/who_weekly.csv", index=False)
        monthly_owid.to_csv("data/processed/owid_monthly.csv", index=False)
        monthly_who.to_csv("data/processed/who_monthly.csv", index=False)
    
    print("\nProcessing Summary:")
    print(f"  Processed OWID: {len(owid_cleaned)} rows")
    print(f"  Processed WHO: {len(who_cleaned)} rows")
    print(f"  Merged dataset: {len(merged_df)} rows")
    print(f"  Weekly aggregation: {len(weekly_owid)} periods")
    print(f"  Monthly aggregation: {len(monthly_owid)} periods")
    
    return owid_cleaned, who_cleaned, merged_df


if __name__ == "__main__":
    # This would be called from main.py after extraction
    print("Data processing module loaded successfully!")

