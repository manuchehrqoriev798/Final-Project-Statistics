"""
Data Extraction Module
Extracts COVID-19 data from OWID and WHO sources
"""

import pandas as pd
import requests
from io import StringIO
import os
from datetime import datetime


def extract_owid_data(url=None, save_path="data/raw/owid_covid_data.csv"):
    """
    Extract COVID-19 data from Our World in Data
    
    Args:
        url: URL to OWID data (default: latest OWID URL)
        save_path: Path to save the extracted data
    
    Returns:
        DataFrame with OWID data
    """
    if url is None:
        url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
    
    print(f"Extracting OWID data from {url}...")
    
    try:
        df = pd.read_csv(url)
        print(f"Successfully extracted {len(df)} rows from OWID")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Save to file
        df.to_csv(save_path, index=False)
        print(f"Data saved to {save_path}")
        
        return df
    except Exception as e:
        print(f"Error extracting OWID data: {e}")
        raise


def extract_who_data(url=None, save_path="data/raw/who_covid_data.csv"):
    """
    Extract COVID-19 data from World Health Organization
    
    Args:
        url: URL to WHO data (default: latest WHO URL)
        save_path: Path to save the extracted data
    
    Returns:
        DataFrame with WHO data
    """
    if url is None:
        url = "https://srhdpeuwpubsa.blob.core.windows.net/whdh/COVID/WHO-COVID-19-global-data.csv"
    
    print(f"Extracting WHO data from {url}...")
    
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        df = pd.read_csv(StringIO(resp.text))
        print(f"Successfully extracted {len(df)} rows from WHO")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Save to file
        df.to_csv(save_path, index=False)
        print(f"Data saved to {save_path}")
        
        return df
    except Exception as e:
        print(f"Error extracting WHO data: {e}")
        raise


def extract_nyt_data(url=None, save_path="data/raw/nyt_covid_data.csv"):
    """
    Extract COVID-19 data from New York Times
    
    Args:
        url: URL to NY Times data (default: latest NY Times URL)
        save_path: Path to save the extracted data
    
    Returns:
        DataFrame with NY Times data
    """
    if url is None:
        url = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us.csv"
    
    print(f"Extracting NY Times data from {url}...")
    
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        df = pd.read_csv(StringIO(resp.text))
        print(f"Successfully extracted {len(df)} rows from NY Times")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Save to file
        df.to_csv(save_path, index=False)
        print(f"Data saved to {save_path}")
        
        return df
    except Exception as e:
        print(f"Error extracting NY Times data: {e}")
        raise


def extract_all_data(country="United States", save_raw=True):
    """
    Extract all data sources (OWID, WHO, NY Times)
    
    Args:
        country: Country to filter (default: United States)
        save_raw: Whether to save raw data files
    
    Returns:
        Tuple of (owid_df, who_df, nyt_df, source_urls)
        source_urls is a dict with 'owid', 'who', 'nyt' keys
    """
    print("=" * 60)
    print("DATA EXTRACTION")
    print("=" * 60)
    
    # Data source URLs
    OWID_URL = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
    WHO_URL = "https://srhdpeuwpubsa.blob.core.windows.net/whdh/COVID/WHO-COVID-19-global-data.csv"
    NYT_URL = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us.csv"
    
    source_urls = {
        'owid': OWID_URL,
        'who': WHO_URL,
        'nyt': NYT_URL
    }
    
    # Extract OWID data
    owid_path = "data/raw/owid_covid_data.csv" if save_raw else None
    owid_df = extract_owid_data(url=OWID_URL, save_path=owid_path)
    
    # Extract WHO data
    who_path = "data/raw/who_covid_data.csv" if save_raw else None
    who_df = extract_who_data(url=WHO_URL, save_path=who_path)
    
    # Extract NY Times data
    nyt_path = "data/raw/nyt_covid_data.csv" if save_raw else None
    nyt_df = extract_nyt_data(url=NYT_URL, save_path=nyt_path)
    
    print("\nExtraction Summary:")
    print(f"  OWID data: {len(owid_df)} rows, {len(owid_df.columns)} columns")
    print(f"  WHO data: {len(who_df)} rows, {len(who_df.columns)} columns")
    print(f"  NY Times data: {len(nyt_df)} rows, {len(nyt_df.columns)} columns")
    print(f"  Target country: {country}")
    
    return owid_df, who_df, nyt_df, source_urls


if __name__ == "__main__":
    # Test extraction
    owid_df, who_df, nyt_df, source_urls = extract_all_data()
    print("\nExtraction completed successfully!")



