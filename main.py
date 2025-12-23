"""
Main Execution Script
Runs the complete analysis pipeline
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from extract_data import extract_all_data
from process_data import process_all_data
from analyze import run_complete_analysis
from generate_html import create_html_dashboard


def main():
    """
    Main execution function
    """
    print("=" * 80)
    print("COVID-19 VACCINATION VS INFECTION ANALYSIS")
    print("Statistics Final Project")
    print("=" * 80)
    print()
    
    # Configuration
    COUNTRY = "United States"
    SAVE_RAW = True
    SAVE_PROCESSED = True
    
    try:
        # Step 1: Extract Data
        print("\n" + "=" * 80)
        print("STEP 1: DATA EXTRACTION")
        print("=" * 80)
        owid_df, who_df, nyt_df, source_urls = extract_all_data(country=COUNTRY, save_raw=SAVE_RAW)
        
        # Step 2: Process Data
        print("\n" + "=" * 80)
        print("STEP 2: DATA PROCESSING")
        print("=" * 80)
        owid_processed, who_processed, merged_df = process_all_data(
            owid_df, who_df, nyt_df, country=COUNTRY, save_processed=SAVE_PROCESSED
        )
        
        # Convert to datetime index if needed
        import pandas as pd
        if 'date' in merged_df.columns:
            merged_df['date'] = pd.to_datetime(merged_df['date'])
            merged_df = merged_df.set_index('date').sort_index()
        
        # Step 3: Statistical Analysis
        print("\n" + "=" * 80)
        print("STEP 3: STATISTICAL ANALYSIS")
        print("=" * 80)
        analysis_results = run_complete_analysis(merged_df)
        
        # Step 4: Create HTML Dashboard
        print("\n" + "=" * 80)
        print("STEP 4: CREATING HTML DASHBOARD")
        print("=" * 80)
        create_html_dashboard(merged_df, analysis_results, source_urls, owid_df, who_df, nyt_df, save_path="index.html")
        
        # Final Summary
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE!")
        print("=" * 80)
        print("\nOutput Files:")
        print("  - Raw Data: data/raw/")
        print("  - Processed Data: data/processed/merged_data_clean_weekly.csv")
        print("  - Interactive Dashboard: index.html")
        
        cond = analysis_results.get("conditional", {})
        p_high = cond.get("p_I_high", 0)
        p_low = cond.get("p_I_low", 0)
        
        print("\nKey Findings:")
        print(f"  - High vaccination days infection probability: {p_high:.4f}")
        print(f"  - Low vaccination days infection probability: {p_low:.4f}")
        
        if p_high < p_low:
            print(f"  - Reduction in infection probability: {abs(p_high - p_low):.4f}")
            print("  - Conclusion: Higher vaccination is associated with lower infection rates")
        else:
            print("  - Note: Results show mixed relationship")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
