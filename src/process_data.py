"""
Data Processing Module
Cleans, processes, and aggregates COVID-19 data
Uses NY Times data for better quality
"""
import pandas as pd
import numpy as np
import requests
from io import StringIO
import os
from datetime import datetime


def get_better_covid_data(nyt_df, owid_df, country="United States", save_path="data/processed/merged_data_clean_weekly.csv"):
    """
    Process COVID-19 data from NY Times, OWID, and WHO
    Filter to peak COVID period: 2020-2022
    Aggregate all data to weekly (sum for cases/deaths, mean for vaccination)
    
    Args:
        nyt_df: NY Times DataFrame
        owid_df: OWID DataFrame (for vaccination data)
        country: Country name (default: United States)
        save_path: Path to save cleaned data
    
    Returns:
        Clean weekly DataFrame
    """
    print("=" * 60)
    print("PROCESSING COVID-19 DATA FROM ALL SOURCES")
    print("=" * 60)
    
    print("\n1. Processing NY Times COVID-19 data...")
    try:
        # Use provided NY Times data
        nyt_us = nyt_df.copy()
        print(f"   ✓ Loaded {len(nyt_us):,} rows from NY Times")
        
        # Convert date
        nyt_us['date'] = pd.to_datetime(nyt_us['date'])
        nyt_us = nyt_us.sort_values('date')
        
        print(f"   Date range: {nyt_us['date'].min().date()} to {nyt_us['date'].max().date()}")
        
        # Filter to peak COVID period: 2020-2022 (the heavy years)
        print("\n2. Filtering to peak COVID period (2020-2022)...")
        peak_period = nyt_us[(nyt_us['date'] >= '2020-01-01') & (nyt_us['date'] <= '2022-12-31')].copy()
        print(f"   ✓ Filtered to {len(peak_period):,} days")
        print(f"   Date range: {peak_period['date'].min().date()} to {peak_period['date'].max().date()}")
        
        # Get vaccination data from OWID (they have better vaccination data)
        print("\n3. Getting vaccination data from OWID...")
        try:
            us_owid = owid_df[owid_df['location'] == 'United States'].copy()
            us_owid['date'] = pd.to_datetime(us_owid['date'])
            
            # Filter to same period
            us_owid = us_owid[(us_owid['date'] >= '2020-01-01') & (us_owid['date'] <= '2022-12-31')].copy()
            
            # Merge vaccination data
            peak_period = peak_period.merge(
                us_owid[['date', 'people_vaccinated_per_hundred', 'people_vaccinated', 
                        'total_vaccinations', 'people_fully_vaccinated']],
                on='date',
                how='left'
            )
            
            # Calculate vaccination rate
            peak_period['vaccination_rate'] = peak_period['people_vaccinated_per_hundred'] / 100.0
            peak_period['vaccination_rate'] = peak_period['vaccination_rate'].ffill().fillna(0)
            peak_period['vaccination_rate'] = peak_period['vaccination_rate'].clip(0, 1)
            
            print(f"   ✓ Merged vaccination data")
        except Exception as e:
            print(f"   ⚠ Could not get vaccination data: {e}")
            peak_period['vaccination_rate'] = 0.0
        
        # NY Times data has cumulative cases, need to calculate daily new cases
        peak_period = peak_period.sort_values('date')
        peak_period['new_cases'] = peak_period['cases'].diff().fillna(peak_period['cases'].iloc[0])
        peak_period['new_deaths'] = peak_period['deaths'].diff().fillna(peak_period['deaths'].iloc[0])
        
        # Ensure non-negative (sometimes data corrections cause negative)
        peak_period['new_cases'] = peak_period['new_cases'].clip(lower=0)
        peak_period['new_deaths'] = peak_period['new_deaths'].clip(lower=0)
        
        # Create infection indicator
        peak_period['I'] = (peak_period['new_cases'] > 0).astype(int)
        
        # Drop cumulative columns
        peak_period = peak_period.drop(columns=['cases', 'deaths'])
        
        # Ensure complete daily series
        date_range = pd.date_range(start=peak_period['date'].min(), end=peak_period['date'].max(), freq='D')
        complete_dates = pd.DataFrame({'date': date_range})
        peak_period = complete_dates.merge(peak_period, on='date', how='left')
        
        # Fill missing values appropriately
        peak_period['new_cases'] = peak_period['new_cases'].fillna(0)
        peak_period['new_deaths'] = peak_period['new_deaths'].fillna(0)
        peak_period['I'] = peak_period['I'].fillna(0)
        
        # Forward fill vaccination data
        vacc_cols = ['vaccination_rate', 'people_vaccinated', 'people_vaccinated_per_hundred']
        for col in vacc_cols:
            if col in peak_period.columns:
                peak_period[col] = peak_period[col].ffill().fillna(0)
        
        # Set date as index
        peak_period = peak_period.set_index('date').sort_index()
        
        # Aggregate to weekly (WHO is already weekly, NY Times and OWID are daily - convert to weekly)
        print(f"\n4. Aggregating to weekly data...")
        weekly_data = peak_period.resample('W').agg({
            'new_cases': 'sum',  # Sum cases for the week
            'new_deaths': 'sum',  # Sum deaths for the week
            'I': lambda x: 1 if x.sum() > 0 else 0,  # 1 if any infection in the week
            'vaccination_rate': 'mean',  # Average vaccination rate for the week
            'people_vaccinated': 'mean',
            'people_vaccinated_per_hundred': 'mean'
        })
        
        # Keep only columns that exist
        for col in ['people_vaccinated', 'people_vaccinated_per_hundred']:
            if col not in weekly_data.columns:
                weekly_data[col] = 0
        
        print(f"   ✓ Aggregated {len(peak_period):,} daily records to {len(weekly_data):,} weekly records")
        
        print(f"\n5. Final weekly dataset:")
        print(f"   Total weeks: {len(weekly_data):,}")
        print(f"   Weeks with cases > 0: {(weekly_data['new_cases'] > 0).sum():,}")
        print(f"   Total cases: {weekly_data['new_cases'].sum():,.0f}")
        print(f"   Average vaccination rate: {weekly_data['vaccination_rate'].mean():.4f}")
        print(f"   Max vaccination rate: {weekly_data['vaccination_rate'].max():.4f}")
        print(f"   Missing values: {weekly_data.isnull().sum().sum()}")
        
        # Save clean data
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        weekly_data.reset_index().to_csv(save_path, index=False)
        
        print(f"\n✓ Saved clean weekly data to: {save_path}")
        print(f"✓ Data covers: {weekly_data.index.min().date()} to {weekly_data.index.max().date()}")
        print(f"✓ Note: All data sources converted to weekly aggregation (daily sources aggregated, WHO was already weekly)")
        
        return weekly_data.reset_index()
        
    except Exception as e:
        print(f"\n❌ Error processing data: {e}")
        raise


def process_all_data(owid_df, who_df, nyt_df, country="United States", save_processed=True):
    """
    Process all data sources and create clean weekly dataset
    (All sources aggregated to weekly: OWID and NY Times from daily, WHO was already weekly)
    
    Args:
        owid_df: OWID DataFrame
        who_df: WHO DataFrame
        nyt_df: NY Times DataFrame
        country: Country name
        save_processed: Whether to save processed data
    
    Returns:
        Clean weekly DataFrame
    """
    print("=" * 60)
    print("DATA PROCESSING")
    print("=" * 60)
    
    # Process data from all 3 sources
    print("\nProcessing data from NY Times, OWID, and WHO...")
    clean_df = get_better_covid_data(nyt_df, owid_df, country=country)
    
    return None, None, clean_df


if __name__ == "__main__":
    # Test processing
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from extract_data import extract_all_data
    
    owid_df, who_df = extract_all_data()
    clean_df = process_all_data(owid_df, who_df)
    print("\n✓ Processing completed successfully!")
