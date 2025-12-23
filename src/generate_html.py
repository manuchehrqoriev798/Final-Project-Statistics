"""
Simple HTML Generator Module
Creates clean HTML dashboard with Canvas charts (no Plotly, no matplotlib)
"""
import pandas as pd
import json
import os


def prepare_chart_data(df, owid_df, who_df, nyt_df):
    """
    Prepare data for simple Canvas charts
    
    Args:
        df: Clean daily DataFrame with date index
        owid_df: Raw OWID DataFrame
        who_df: Raw WHO DataFrame
        nyt_df: Raw NY Times DataFrame
    
    Returns:
        Dictionary with chart data
    """
    # Calculate statistics
    p_I = df['I'].mean()
    p_V = df['vaccination_rate'].mean()
    high_vax = df[df['vaccination_rate'] >= 0.5]
    low_vax = df[df['vaccination_rate'] < 0.5]
    p_I_high = high_vax['I'].mean() if len(high_vax) > 0 else 0
    p_I_low = low_vax['I'].mean() if len(low_vax) > 0 else 0
    
    # Prepare data for 3-source comparison chart - ALL SOURCES ARE NOW WEEKLY
    # Convert all sources to weekly aggregation for comparison
    
    # OWID: US data, new_cases - aggregate daily to weekly
    owid_us = owid_df[owid_df['location'] == 'United States'].copy()
    if 'date' in owid_us.columns:
        owid_us['date'] = pd.to_datetime(owid_us['date'])
        owid_us = owid_us.set_index('date').sort_index()
        owid_us = owid_us[(owid_us.index >= '2020-01-01') & (owid_us.index <= '2022-12-31')]
        # Aggregate to weekly (sum of new_cases)
        owid_weekly = owid_us['new_cases'].resample('W').sum().fillna(0)
        owid_dates = [d.strftime('%Y-%m-%d') for d in owid_weekly.index]
        owid_values = [float(v) if pd.notna(v) else 0.0 for v in owid_weekly.values]
    else:
        owid_dates, owid_values = [], []
    
    # WHO: US data, New_cases - already weekly
    who_us = who_df[who_df['Country'] == 'United States of America'].copy()
    if 'Date_reported' in who_us.columns:
        who_us['Date_reported'] = pd.to_datetime(who_us['Date_reported'])
        who_us = who_us.set_index('Date_reported').sort_index()
        who_us = who_us[(who_us.index >= '2020-01-01') & (who_us.index <= '2022-12-31')]
        # WHO is already weekly
        who_weekly = who_us['New_cases'].fillna(0)
        who_dates = [d.strftime('%Y-%m-%d') for d in who_weekly.index]
        who_values = [float(v) if pd.notna(v) else 0.0 for v in who_weekly.values]
    else:
        who_dates, who_values = [], []
    
    # NY Times: convert cumulative to daily, then aggregate to weekly
    nyt_copy = nyt_df.copy()
    if 'date' in nyt_copy.columns:
        nyt_copy['date'] = pd.to_datetime(nyt_copy['date'])
        nyt_copy = nyt_copy.sort_values('date')
        nyt_copy = nyt_copy[(nyt_copy['date'] >= '2020-01-01') & (nyt_copy['date'] <= '2022-12-31')]
        # Convert cumulative to daily
        nyt_copy['new_cases'] = nyt_copy['cases'].diff().fillna(nyt_copy['cases'].iloc[0]).clip(lower=0)
        nyt_copy = nyt_copy.set_index('date')
        # Aggregate to weekly (sum of new_cases)
        nyt_weekly = nyt_copy['new_cases'].resample('W').sum().fillna(0)
        nyt_dates = [pd.to_datetime(d).strftime('%Y-%m-%d') for d in nyt_weekly.index]
        nyt_values = [float(v) if pd.notna(v) else 0.0 for v in nyt_weekly.values]
    else:
        nyt_dates, nyt_values = [], []
    
    # Align dates across all 3 sources
    # Create dictionaries for alignment
    owid_dict = dict(zip(owid_dates, owid_values)) if owid_dates else {}
    who_dict = dict(zip(who_dates, who_values)) if who_dates else {}
    nyt_dict = dict(zip(nyt_dates, nyt_values)) if nyt_dates else {}
    
    # Find common dates - all sources are now weekly, match within 7 days (one week tolerance)
    # Use intersection of all three sources
    if owid_dict and nyt_dict and who_dict:
        # Find dates where all three have data (within 7 days)
        all_dates_set = set(owid_dates) | set(nyt_dates) | set(who_dates)
        base_dates = []
        for d in sorted(all_dates_set):
            pd_date = pd.to_datetime(d)
            # Check if we can match within 7 days for all three
            has_owid = any(abs((pd.to_datetime(od) - pd_date).days) <= 7 for od in owid_dates)
            has_nyt = any(abs((pd.to_datetime(nd) - pd_date).days) <= 7 for nd in nyt_dates)
            has_who = any(abs((pd.to_datetime(wd) - pd_date).days) <= 7 for wd in who_dates)
            if has_owid and has_nyt and has_who:
                base_dates.append(d)
    elif owid_dict and nyt_dict:
        base_dates = sorted(set(owid_dates) & set(nyt_dates))
    elif owid_dict:
        base_dates = sorted(owid_dates)
    elif nyt_dict:
        base_dates = sorted(nyt_dates)
    else:
        base_dates = []
    
    # Use base dates for comparison, match values within 7 days (one week tolerance for weekly data)
    comparison_dates = base_dates[:200] if len(base_dates) > 200 else base_dates
    
    # Match all three sources (within 7 days for weekly data)
    def match_weekly_value(date_str, source_dict, source_dates):
        """Match value within 7 days for weekly data"""
        pd_date = pd.to_datetime(date_str)
        matched_val = source_dict.get(date_str, 0.0)  # Try exact match first
        if matched_val == 0.0 or date_str not in source_dict:
            min_diff = float('inf')
            best_val = 0.0
            for src_date_str, src_val in source_dict.items():
                src_date = pd.to_datetime(src_date_str)
                diff = abs((pd_date - src_date).days)
                if diff <= 7 and diff < min_diff:
                    best_val = src_val
                    min_diff = diff
            if min_diff != float('inf'):
                matched_val = best_val
        return matched_val
    
    comparison_owid = [match_weekly_value(d, owid_dict, owid_dates) for d in comparison_dates]
    comparison_nyt = [match_weekly_value(d, nyt_dict, nyt_dates) for d in comparison_dates]
    comparison_who = [match_weekly_value(d, who_dict, who_dates) for d in comparison_dates] if who_dict else [0.0] * len(comparison_dates)
    
    # Prepare data
    chart_data = {
        'dataCoverage': {
            'start': df.index.min().strftime('%B %d, %Y'),
            'end': df.index.max().strftime('%B %d, %Y'),
            'totalDays': len(df)
        },
        'vaccinationTimeline': {
            'dates': [d.strftime('%Y-%m-%d') for d in df.index],  # Already weekly data
            'rates': [float(v) for v in df['vaccination_rate'].values],
            'weekNumbers': [f'Week {i+1}' for i in range(len(df.index))]
        },
        'threeSourceComparison': {
            'dates': comparison_dates,
            'weekNumbers': [f'Week {i+1}' for i in range(len(comparison_dates))],
            'owid': comparison_owid,
            'who': comparison_who,
            'nyt': comparison_nyt
        },
        'conditionalProbabilities': {
            'highVax': float(p_I_high),
            'lowVax': float(p_I_low)
        },
        'descriptiveStats': {
            'mean': float(df['new_cases'].mean()),
            'median': float(df['new_cases'].median()),
            'std': float(df['new_cases'].std())
        },
        'bernoulli': {
            'p_I': float(p_I),
            'p_I_0': float(1 - p_I)
        }
    }
    
    return chart_data


def create_html_dashboard(df, analysis_results, source_urls, owid_df, who_df, nyt_df, save_path="index.html"):
    """
    Create simple HTML dashboard with Canvas charts
    
    Args:
        df: Clean daily DataFrame
        analysis_results: Analysis results dictionary
        source_urls: Dictionary with 'owid', 'who', 'nyt' URLs
        save_path: Path to save HTML file
    """
    chart_data = prepare_chart_data(df, owid_df, who_df, nyt_df)
    
    # Get correlation analysis results (main hypothesis test)
    corr_analysis = analysis_results.get("correlation_analysis", {})
    correlation = corr_analysis.get("correlation_coefficient", 0)
    corr_p_value = corr_analysis.get("p_value", 1.0)
    corr_t_stat = corr_analysis.get("t_statistic", 0)
    corr_significant = corr_analysis.get("significant", False)
    
    # Determine conclusion based on correlation
    if corr_significant:
        conclusion = "REJECT H₀"
        if correlation > 0:
            conclusion_text = "A significant positive correlation was found (r = {:.4f}, p = {:.4f}). However, this reflects temporal confounding where higher vaccination periods coincided with more transmissible variants (Delta, Omicron), rather than indicating that vaccination increases transmission. This demonstrates the importance of controlling for confounding variables in epidemiological analysis.".format(correlation, corr_p_value)
        else:
            conclusion_text = "A significant negative correlation was found, indicating that higher vaccination rates are associated with lower case counts."
    else:
        conclusion = "FAIL TO REJECT H₀"
        conclusion_text = "No significant correlation was found between vaccination rates and weekly case counts (r = {:.4f}, p = {:.4f}).".format(correlation, corr_p_value)
    
    # Keep conditional probability for reference charts
    cond = analysis_results.get("conditional", {})
    p_high = cond.get("p_I_high", chart_data['conditionalProbabilities']['highVax'])
    p_low = cond.get("p_I_low", chart_data['conditionalProbabilities']['lowVax'])
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>COVID-19 Vaccination vs Infection Analysis Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            background-attachment: fixed;
            color: #1a1a1a;
            padding: 20px;
        }}
        .container {{
            max-width: 1500px;
            margin: 40px auto;
            background: rgba(255, 255, 255, 0.98);
            padding: 50px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 42px;
            font-weight: 800;
            margin-bottom: 15px;
        }}
        h2 {{
            text-align: center;
            color: #6c757d;
            font-size: 22px;
            font-weight: 500;
            margin-bottom: 50px;
        }}
        .info-box {{
            background: linear-gradient(135deg, rgba(255, 193, 7, 0.15) 0%, rgba(255, 152, 0, 0.15) 100%);
            border: 2px solid rgba(255, 193, 7, 0.4);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 40px;
            text-align: center;
        }}
        .info-box p {{
            color: #2c3e50;
            font-size: 16px;
            line-height: 1.8;
        }}
        .data-coverage {{
            background: linear-gradient(135deg, rgba(6, 167, 125, 0.15) 0%, rgba(13, 115, 119, 0.15) 100%);
            border: 2px solid rgba(6, 167, 125, 0.4);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 40px;
        }}
        .data-coverage h3 {{
            color: #06A77D;
            font-size: 20px;
            margin-bottom: 15px;
            text-align: center;
        }}
        .data-coverage p {{
            color: #2c3e50;
            font-size: 16px;
            line-height: 1.8;
            margin-bottom: 10px;
        }}
        .sources-section {{
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            border: 2px solid rgba(102, 126, 234, 0.3);
            padding: 30px;
            border-radius: 16px;
            margin: 40px 0;
        }}
        .sources-section h3 {{
            color: #667eea;
            font-size: 24px;
            margin-bottom: 20px;
        }}
        .source-item {{
            margin: 20px 0;
            padding: 15px;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .source-item strong {{
            color: #667eea;
            font-size: 18px;
        }}
        .source-item a {{
            color: #06A77D;
            text-decoration: none;
            word-break: break-all;
            display: inline-block;
            margin-top: 5px;
        }}
        .source-item a:hover {{
            text-decoration: underline;
        }}
        .data-links {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid rgba(6, 167, 125, 0.3);
            text-align: center;
        }}
        .data-links a {{
            color: #06A77D;
            text-decoration: none;
            margin: 0 15px;
            font-weight: 600;
            padding: 10px 20px;
            background: rgba(6, 167, 125, 0.1);
            border-radius: 6px;
            display: inline-block;
            transition: all 0.3s;
        }}
        .data-links a:hover {{
            background: rgba(6, 167, 125, 0.2);
            transform: translateY(-2px);
        }}
        .chart-container {{
            background: #ffffff;
            padding: 30px;
            border-radius: 16px;
            margin: 30px 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .chart-title {{
            font-size: 24px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 20px;
            text-align: center;
        }}
        canvas {{
            width: 100%;
            height: 400px;
            display: block;
        }}
        .hypothesis-box, .conclusion-box {{
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            border: 2px solid rgba(102, 126, 234, 0.3);
            padding: 40px;
            border-radius: 16px;
            margin: 40px 0;
        }}
        .hypothesis-box h2, .conclusion-box h2 {{
            color: #667eea;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 20px;
            text-align: left;
        }}
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 25px;
            margin: 40px 0;
        }}
        .stat-box {{
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            padding: 30px;
            border-radius: 16px;
            border: 2px solid rgba(46, 134, 171, 0.2);
            text-align: center;
        }}
        .stat-value {{
            font-size: 42px;
            font-weight: 800;
            background: linear-gradient(135deg, #2E86AB 0%, #06A77D 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        .stat-label {{
            font-size: 16px;
            color: #6c757d;
            font-weight: 500;
        }}
        .viz-explanation {{
            padding: 20px;
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            border-radius: 12px;
            margin-top: 20px;
        }}
        .viz-explanation h3 {{
            color: #06A77D;
            font-size: 18px;
            margin-bottom: 10px;
        }}
        .viz-explanation p {{
            color: #495057;
            line-height: 1.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>COVID-19 Vaccination vs Infection Analysis</h1>
        <h2>Statistical Analysis Dashboard</h2>
        
        <div class="info-box">
            <p><strong></strong> This website is automatically generated from the latest data. When the data sources are updated and the script is run, this website will be automatically updated with the new information.</p>
        </div>
        
        <div class="hypothesis-box">
            <h2>Research Hypothesis</h2>
            <p style="font-size: 18px; line-height: 1.9;">
                <strong>Research Question:</strong> Is there a significant relationship between vaccination rates and weekly new case counts?<br><br>
                <strong>Hypothesis:</strong> There is a significant correlation between vaccination rate and weekly new case counts across the analysis period (2020-2022).<br><br>
                <strong>Statistical Test:</strong> Pearson correlation test (tests whether correlation is significantly different from zero)
            </p>
        </div>
        
        <div class="sources-section">
            <h3>📊 Data Sources</h3>
            <p style="margin-bottom: 20px; color: #495057; font-size: 16px;">
                This analysis uses data from three reliable sources:
            </p>
            <div class="source-item">
                <strong>1. Our World in Data (OWID)</strong><br>
                <a href="{source_urls.get('owid', '#')}" target="_blank">{source_urls.get('owid', 'N/A')}</a>
            </div>
            <div class="source-item">
                <strong>2. World Health Organization (WHO)</strong><br>
                <a href="{source_urls.get('who', '#')}" target="_blank">{source_urls.get('who', 'N/A')}</a>
            </div>
            <div class="source-item">
                <strong>3. New York Times COVID-19 Data</strong><br>
                <a href="{source_urls.get('nyt', '#')}" target="_blank">{source_urls.get('nyt', 'N/A')}</a>
            </div>
            <div class="data-links">
                <a href="data/raw/owid_covid_data.csv" download>📁 Download Raw OWID Data</a>
                <a href="data/raw/who_covid_data.csv" download>📁 Download Raw WHO Data</a>
                <a href="data/raw/nyt_covid_data.csv" download>📁 Download Raw NY Times Data</a>
                <a href="data/processed/merged_data_clean_weekly.csv" download>📁 Download Processed Data (Weekly)</a>
            </div>
        </div>
        
        <div class="data-coverage">
            <h3>📅 Data Coverage Information</h3>
            <p><strong>Data Source:</strong> Combined data from OWID, WHO, and New York Times</p>
            <p><strong>Coverage Period:</strong> {chart_data['dataCoverage']['start']} to {chart_data['dataCoverage']['end']}</p>
            <p><strong>Total Days:</strong> {chart_data['dataCoverage']['totalDays']:,} days</p>
            <p><strong>Data Frequency:</strong> Weekly (All data sources have been converted to weekly aggregation for consistency)</p>
            <p><strong>Data Aggregation Note:</strong> 
            <ul style="margin-left: 20px; margin-top: 10px;">
                <li><strong>OWID:</strong> Originally daily data, aggregated to weekly (sum of cases per week)</li>
                <li><strong>NY Times:</strong> Originally daily data, aggregated to weekly (sum of cases per week)</li>
                <li><strong>WHO:</strong> Originally weekly data, used as-is</li>
            </ul>
            </p>
            <p><strong>Geographic Coverage:</strong> United States (While the original data sources contain data for multiple countries, this analysis focuses on the United States during the peak COVID-19 period from 2020 to 2022)</p>
        </div>
        
        <div class="stat-grid">
            <div class="stat-box">
                <div class="stat-value">{chart_data['descriptiveStats']['mean']:,.0f}</div>
                <div class="stat-label">Mean Weekly Cases</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{chart_data['descriptiveStats']['median']:,.0f}</div>
                <div class="stat-label">Median Weekly Cases</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{chart_data['descriptiveStats']['std']:,.0f}</div>
                <div class="stat-label">Standard Deviation</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{chart_data['bernoulli']['p_I']:.3f}</div>
                <div class="stat-label">Infection Probability</div>
            </div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">1. Vaccination Rate Over Time</div>
            <canvas id="chart1"></canvas>
            <div class="viz-explanation">
                <h3>What it shows:</h3>
                <p>This chart displays how the vaccination coverage rate changed over time from 2020 to 2022. The blue line represents the proportion of the population that was vaccinated. The red dashed horizontal line at 0.5 (50%) is the threshold we use to classify periods as "high vaccination" (above the line) or "low vaccination" (below the line).</p>
            </div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">2. Weekly New Cases: Comparison Across All 3 Data Sources</div>
            <canvas id="chart2"></canvas>
            <div class="viz-explanation">
                <h3>What it shows:</h3>
                <p>This chart compares weekly new COVID-19 cases from all three data sources (OWID in blue, WHO in orange, NY Times in green). All three sources are displayed as weekly data for consistency: OWID and NY Times were aggregated from daily to weekly (sum of cases per week), while WHO was already weekly. This visualization allows us to compare how different data sources report the same metric and validate data consistency across sources.</p>
            </div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">3. Conditional Probabilities Comparison</div>
            <canvas id="chart3"></canvas>
            <div class="viz-explanation">
                <h3>What it shows:</h3>
                <p>This bar chart directly compares the infection probability during two different periods: high vaccination (green bar, V ≥ 0.5) and low vaccination (orange bar, V < 0.5). The height of each bar represents the probability of infection occurring. If vaccination is effective, we expect the green bar (high vaccination) to be lower than the orange bar (low vaccination). The difference between these bars is the key evidence for our hypothesis.</p>
            </div>
        </div>
        
        <div class="conclusion-box">
            <h2>Hypothesis Testing Results & Conclusion</h2>
            <div style="font-size: 18px; line-height: 1.8;">
                <p><strong>Statistical Test Results (Correlation Analysis):</strong></p>
                <ul style="line-height: 2; margin-left: 20px;">
                    <li><strong>Test:</strong> Pearson correlation test</li>
                    <li><strong>Correlation Coefficient (r):</strong> {correlation:.4f}</li>
                    <li><strong>T-statistic:</strong> {corr_t_stat:.4f}</li>
                    <li><strong>P-value:</strong> {corr_p_value:.6f}</li>
                    <li><strong>Significance Level (α):</strong> 0.05</li>
                    <li><strong>Result:</strong> {conclusion}</li>
                </ul>
                <p style="margin-top: 25px;"><strong>Key Findings:</strong></p>
                <ul style="line-height: 2; margin-left: 20px;">
                    <li>Correlation coefficient: <strong>{correlation:.4f}</strong> ({'positive' if correlation > 0 else 'negative' if correlation < 0 else 'zero'} correlation)</li>
                    <li>Statistical significance: <strong>{'Significant' if corr_significant else 'Not significant'}</strong> (p = {corr_p_value:.4f})</li>
                    <li>Sample size: <strong>{corr_analysis.get('sample_size', 'N/A')}</strong> weeks</li>
                </ul>
                <p style="margin-top: 25px; font-size: 20px; font-weight: bold;">
                    CONCLUSION: {conclusion_text}
                </p>
                <p style="margin-top: 25px; font-size: 16px; line-height: 1.9;">
                    <strong>What Our Results Mean (In Simple Words):</strong><br>
                    We found a significant positive correlation (r = {correlation:.4f}), meaning when vaccination rates went UP, case counts also went UP. This seems backwards! But here's why it makes sense: Vaccination increased over time (2020 to 2022), and during that same period, new variants (Delta, Omicron) caused huge case surges. So both vaccination AND cases increased at the same time - not because vaccination caused cases, but because of timing. This is called "temporal confounding" - when two things happen at the same time but aren't actually related. Think of it like this: More people use umbrellas when it rains, but umbrellas don't cause rain!
                </p>
                
                <div style="margin-top: 40px; padding: 30px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); border-left: 4px solid #667eea; border-radius: 8px;">
                    <h3 style="color: #667eea; margin-bottom: 20px; font-size: 22px;">Research Context & Comparison with Published Studies</h3>
                    <p style="font-size: 16px; line-height: 1.9; margin-bottom: 20px;">
                        Published research by Au (2022) found that <strong>higher vaccination rates predict reduction in SARS-CoV-2 transmission</strong> when using sophisticated statistical methods that control for temporal confounding factors (previous incidence, testing frequency, mask usage, month effects, etc.). 
                    </p>
                    <p style="font-size: 16px; line-height: 1.9; margin-bottom: 20px;">
                        In contrast, our simple correlation analysis (without such controls) finds a positive correlation (r = {correlation:.4f}), which demonstrates the exact temporal confounding effect that Au (2022) warned about. The researchers explicitly stated: <em>"Without this transformation, a spurious correlation would occur in which incidence would appear to rise even as vaccination rates increase over the summer."</em>
                    </p>
                    <p style="font-size: 16px; line-height: 1.9;">
                        This contrast highlights the critical importance of controlling for confounding variables in epidemiological analysis. Our findings validate the researchers' warning and demonstrate why sophisticated statistical modeling is essential for drawing accurate conclusions about vaccine effectiveness.
                    </p>
                    <p style="margin-top: 20px; font-size: 14px; font-style: italic;">
                        Source: <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC8938221/" target="_blank" style="color: #06A77D; font-weight: 600;">Au, J. Higher vaccination rates predict reduction in SARS-CoV-2 transmission across the United States</a> (<em>Infection</em>, 50:1255-1266, PMCID: PMC8938221)
                    </p>
                </div>
                
                <div style="margin-top: 40px; padding: 30px; background: linear-gradient(135deg, rgba(46, 134, 171, 0.1) 0%, rgba(6, 167, 125, 0.1) 100%); border-left: 4px solid #2E86AB; border-radius: 8px;">
                    <h3 style="color: #2E86AB; margin-bottom: 20px; font-size: 22px;">Next Steps & Future Research Directions</h3>
                    <p style="font-size: 16px; line-height: 1.9; margin-bottom: 15px;">
                        <strong>1. Extended Geographic Analysis:</strong> Replicate this analysis across different countries and continents to examine whether the temporal confounding patterns observed in the United States are consistent globally. Different regions may show different relationships depending on variant emergence timing, vaccination rollout speed, and local public health policies.
                    </p>
                    <p style="font-size: 16px; line-height: 1.9; margin-bottom: 15px;">
                        <strong>2. Advanced Statistical Modeling:</strong> Apply the sophisticated statistical methods used in published research (panel data regression with temporal controls, fixed/random effects models) to our dataset to properly account for confounding variables and estimate the true effect of vaccination on transmission reduction.
                    </p>
                    <p style="font-size: 16px; line-height: 1.9; margin-bottom: 15px;">
                        <strong>3. Distribution Fitting:</strong> Fit appropriate probability distributions (e.g., Poisson, Negative Binomial) to weekly case counts to better understand the underlying data generation process and improve statistical modeling accuracy.
                    </p>
                    <p style="font-size: 16px; line-height: 1.9;">
                        <strong>4. Variant-Specific Analysis:</strong> Segment the data by variant periods (Alpha, Delta, Omicron) to examine whether vaccination effectiveness differs across variants and to better control for variant-specific confounding effects.
                    </p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Chart data
        const chartData = {json.dumps(chart_data, indent=8)};
        
        // Simple line chart function
        function drawLineChart(canvasId, data, options) {{
            const canvas = document.getElementById(canvasId);
            const ctx = canvas.getContext('2d');
            const width = canvas.width = canvas.offsetWidth;
            const height = canvas.height = 400;
            
            const padding = {{ top: 40, right: 40, bottom: 60, left: 80 }};
            const chartWidth = width - padding.left - padding.right;
            const chartHeight = height - padding.top - padding.bottom;
            
            ctx.clearRect(0, 0, width, height);
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, width, height);
            
            if (!data || data.length === 0) return;
            
            const values = data.map(d => d[1]);
            const minVal = Math.min(...values);
            const maxVal = Math.max(...values);
            const range = maxVal - minVal || 1;
            
            // Draw grid
            ctx.strokeStyle = '#e0e0e0';
            ctx.lineWidth = 1;
            for (let i = 0; i <= 5; i++) {{
                const y = padding.top + (chartHeight / 5) * i;
                ctx.beginPath();
                ctx.moveTo(padding.left, y);
                ctx.lineTo(width - padding.right, y);
                ctx.stroke();
            }}
            
            // Draw line
            ctx.strokeStyle = options.color || '#2E86AB';
            ctx.lineWidth = 3;
            ctx.beginPath();
            
            data.forEach((point, i) => {{
                const x = padding.left + (chartWidth / (data.length - 1)) * i;
                const y = padding.top + chartHeight - ((point[1] - minVal) / range) * chartHeight;
                if (i === 0) {{
                    ctx.moveTo(x, y);
                }} else {{
                    ctx.lineTo(x, y);
                }}
            }});
            ctx.stroke();
            
            // Fill area
            if (options.fill) {{
                ctx.lineTo(padding.left + chartWidth, padding.top + chartHeight);
                ctx.lineTo(padding.left, padding.top + chartHeight);
                ctx.closePath();
                ctx.fillStyle = options.fillColor || 'rgba(46, 134, 171, 0.2)';
                ctx.fill();
            }}
            
            // Draw threshold line
            if (options.threshold !== undefined) {{
                const threshY = padding.top + chartHeight - ((options.threshold - minVal) / range) * chartHeight;
                ctx.strokeStyle = '#dc3545';
                ctx.lineWidth = 2;
                ctx.setLineDash([5, 5]);
                ctx.beginPath();
                ctx.moveTo(padding.left, threshY);
                ctx.lineTo(width - padding.right, threshY);
                ctx.stroke();
                ctx.setLineDash([]);
            }}
            
            // Draw points
            ctx.fillStyle = options.color || '#2E86AB';
            data.forEach((point, i) => {{
                const x = padding.left + (chartWidth / (data.length - 1)) * i;
                const y = padding.top + chartHeight - ((point[1] - minVal) / range) * chartHeight;
                ctx.beginPath();
                ctx.arc(x, y, 4, 0, Math.PI * 2);
                ctx.fill();
            }});
            
            // Draw labels
            ctx.fillStyle = '#2c3e50';
            ctx.font = '12px Inter, sans-serif';
            ctx.textAlign = 'right';
            
            // Y-axis labels
            for (let i = 0; i <= 5; i++) {{
                const val = minVal + (range / 5) * (5 - i);
                const y = padding.top + (chartHeight / 5) * i;
                ctx.fillText(val.toFixed(2), padding.left - 10, y + 4);
            }}
            
            // X-axis labels (week numbers)
            ctx.textAlign = 'center';
            ctx.font = '11px Inter, sans-serif';
            const weekLabels = options.weekNumbers || [];
            const labelStep = Math.max(1, Math.floor(data.length / 10)); // Show ~10 labels
            for (let i = 0; i < data.length; i += labelStep) {{
                const x = padding.left + (chartWidth / (data.length - 1)) * i;
                const label = weekLabels[i] || `Week ${{i+1}}`;
                ctx.fillText(label, x, height - 20);
            }}
            // X-axis title
            ctx.font = '14px Inter, sans-serif';
            ctx.fillText(options.xLabel || 'Week', width / 2, height - 5);
            
            // Y-axis label
            ctx.save();
            ctx.translate(20, height / 2);
            ctx.rotate(-Math.PI / 2);
            ctx.fillText(options.yLabel || 'Value', 0, 0);
            ctx.restore();
        }}
        
        // Multi-line chart function for comparing 3 data sources
        function drawMultiLineChart(canvasId, dates, datasets, options) {{
            const canvas = document.getElementById(canvasId);
            const ctx = canvas.getContext('2d');
            const width = canvas.width = canvas.offsetWidth;
            const height = canvas.height = 400;
            
            const padding = {{ top: 40, right: 150, bottom: 60, left: 80 }};
            const chartWidth = width - padding.left - padding.right;
            const chartHeight = height - padding.top - padding.bottom;
            
            ctx.clearRect(0, 0, width, height);
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, width, height);
            
            if (!dates || dates.length === 0) return;
            
            // Find min/max across all datasets
            let minVal = Infinity;
            let maxVal = -Infinity;
            datasets.forEach(dataset => {{
                dataset.values.forEach(val => {{
                    if (val < minVal) minVal = val;
                    if (val > maxVal) maxVal = val;
                }});
            }});
            const range = maxVal - minVal || 1;
            
            // Draw grid
            ctx.strokeStyle = '#e0e0e0';
            ctx.lineWidth = 1;
            for (let i = 0; i <= 5; i++) {{
                const y = padding.top + (chartHeight / 5) * i;
                ctx.beginPath();
                ctx.moveTo(padding.left, y);
                ctx.lineTo(width - padding.right, y);
                ctx.stroke();
            }}
            
            // Draw lines for each dataset
            datasets.forEach(dataset => {{
                ctx.strokeStyle = dataset.color;
                ctx.lineWidth = 3;
                ctx.beginPath();
                
                dataset.values.forEach((value, i) => {{
                    const x = padding.left + (chartWidth / (dates.length - 1)) * i;
                    const y = padding.top + chartHeight - ((value - minVal) / range) * chartHeight;
                    if (i === 0) {{
                        ctx.moveTo(x, y);
                    }} else {{
                        ctx.lineTo(x, y);
                    }}
                }});
                ctx.stroke();
                
                // Draw points
                ctx.fillStyle = dataset.color;
                dataset.values.forEach((value, i) => {{
                    const x = padding.left + (chartWidth / (dates.length - 1)) * i;
                    const y = padding.top + chartHeight - ((value - minVal) / range) * chartHeight;
                    ctx.beginPath();
                    ctx.arc(x, y, 3, 0, Math.PI * 2);
                    ctx.fill();
                }});
            }});
            
            // Draw legend
            ctx.font = '14px Inter, sans-serif';
            datasets.forEach((dataset, i) => {{
                const x = width - padding.right + 10;
                const y = padding.top + 20 + i * 25;
                ctx.fillStyle = dataset.color;
                ctx.fillRect(x, y - 10, 15, 3);
                ctx.fillStyle = '#2c3e50';
                ctx.textAlign = 'left';
                ctx.fillText(dataset.label, x + 20, y);
            }});
            
            // Draw labels
            ctx.fillStyle = '#2c3e50';
            ctx.font = '12px Inter, sans-serif';
            ctx.textAlign = 'right';
            
            // Y-axis labels
            for (let i = 0; i <= 5; i++) {{
                const val = minVal + (range / 5) * (5 - i);
                const y = padding.top + (chartHeight / 5) * i;
                ctx.fillText(val.toFixed(0), padding.left - 10, y + 4);
            }}
            
            // X-axis labels (week numbers)
            ctx.textAlign = 'center';
            ctx.font = '11px Inter, sans-serif';
            const weekLabels = options.weekNumbers || [];
            const labelStep = Math.max(1, Math.floor(dates.length / 10)); // Show ~10 labels
            for (let i = 0; i < dates.length; i += labelStep) {{
                const x = padding.left + (chartWidth / (dates.length - 1)) * i;
                const label = weekLabels[i] || `Week ${{i+1}}`;
                ctx.fillText(label, x, height - 20);
            }}
            // X-axis title
            ctx.font = '14px Inter, sans-serif';
            ctx.fillText(options.xLabel || 'Week', width / 2, height - 5);
            
            // Y-axis label
            ctx.save();
            ctx.translate(20, height / 2);
            ctx.rotate(-Math.PI / 2);
            ctx.fillText(options.yLabel || 'Value', 0, 0);
            ctx.restore();
        }}
        
        // Enhanced bar chart function for conditional probabilities (better design)
        function drawBarChart(canvasId, labels, values, colors) {{
            const canvas = document.getElementById(canvasId);
            const ctx = canvas.getContext('2d');
            const width = canvas.width = canvas.offsetWidth;
            const height = canvas.height = 400;
            
            const padding = {{ top: 40, right: 40, bottom: 100, left: 80 }};
            const chartWidth = width - padding.left - padding.right;
            const chartHeight = height - padding.top - padding.bottom;
            const barWidth = chartWidth / labels.length * 0.6;
            const barSpacing = chartWidth / labels.length;
            
            ctx.clearRect(0, 0, width, height);
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, width, height);
            
            const maxVal = Math.max(...values);
            
            // Draw grid
            ctx.strokeStyle = '#e0e0e0';
            ctx.lineWidth = 1;
            for (let i = 0; i <= 5; i++) {{
                const y = padding.top + (chartHeight / 5) * i;
                ctx.beginPath();
                ctx.moveTo(padding.left, y);
                ctx.lineTo(width - padding.right, y);
                ctx.stroke();
            }}
            
            // Draw bars with better styling
            labels.forEach((label, i) => {{
                const barHeight = (values[i] / maxVal) * chartHeight;
                const x = padding.left + i * barSpacing + (barSpacing - barWidth) / 2;
                const y = padding.top + chartHeight - barHeight;
                
                // Draw bar with gradient effect
                const gradient = ctx.createLinearGradient(x, y, x, padding.top + chartHeight);
                gradient.addColorStop(0, colors[i] || '#2E86AB');
                gradient.addColorStop(1, colors[i] + 'CC' || '#2E86ABCC');
                ctx.fillStyle = gradient;
                ctx.fillRect(x, y, barWidth, barHeight);
                
                // Draw border
                ctx.strokeStyle = colors[i] || '#2E86AB';
                ctx.lineWidth = 2;
                ctx.strokeRect(x, y, barWidth, barHeight);
                
                // Draw value label on top
                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 16px Inter, sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText(values[i].toFixed(4), x + barWidth / 2, y - 8);
                
                // Draw label below
                ctx.fillStyle = '#2c3e50';
                ctx.font = '14px Inter, sans-serif';
                const labelLines = label.split('\\n');
                labelLines.forEach((line, j) => {{
                    ctx.fillText(line, x + barWidth / 2, padding.top + chartHeight + 25 + j * 18);
                }});
            }});
            
            // Draw y-axis labels
            ctx.strokeStyle = '#e0e0e0';
            ctx.lineWidth = 1;
            for (let i = 0; i <= 5; i++) {{
                const val = (maxVal / 5) * (5 - i);
                const y = padding.top + (chartHeight / 5) * i;
                ctx.fillStyle = '#2c3e50';
                ctx.textAlign = 'right';
                ctx.font = '12px Inter, sans-serif';
                ctx.fillText(val.toFixed(2), padding.left - 10, y + 4);
            }}
            
            // Draw y-axis title
            ctx.save();
            ctx.translate(20, height / 2);
            ctx.rotate(-Math.PI / 2);
            ctx.fillStyle = '#2c3e50';
            ctx.font = '14px Inter, sans-serif';
            ctx.fillText('Infection Probability', 0, 0);
            ctx.restore();
        }}
        
        // Initialize charts when page loads
        window.addEventListener('load', function() {{
            // Chart 1: Vaccination Rate
            const vaccData = chartData.vaccinationTimeline.dates.map((d, i) => [d, chartData.vaccinationTimeline.rates[i]]);
            drawLineChart('chart1', vaccData, {{
                color: '#2E86AB',
                fill: true,
                fillColor: 'rgba(46, 134, 171, 0.2)',
                threshold: 0.5,
                xLabel: 'Week',
                weekNumbers: chartData.vaccinationTimeline.weekNumbers,
                yLabel: 'Vaccination Rate'
            }});
            
            // Chart 2: Three Source Comparison (Daily Data)
            drawMultiLineChart('chart2', chartData.threeSourceComparison.dates, [
                {{label: 'OWID', values: chartData.threeSourceComparison.owid, color: '#2E86AB'}},
                {{label: 'WHO', values: chartData.threeSourceComparison.who, color: '#F18F01'}},
                {{label: 'NY Times', values: chartData.threeSourceComparison.nyt, color: '#06A77D'}}
            ], {{
                xLabel: 'Week',
                weekNumbers: chartData.threeSourceComparison.weekNumbers,
                yLabel: 'Weekly New Cases'
            }});
            
            // Chart 3: Conditional Probabilities (enhanced design)
            drawBarChart('chart3', 
                ['High Vaccination\\n(V ≥ 0.5)', 'Low Vaccination\\n(V < 0.5)'],
                [chartData.conditionalProbabilities.highVax, chartData.conditionalProbabilities.lowVax],
                ['#06A77D', '#F18F01']
            );
        }});
    </script>
</body>
</html>"""
    
    # Create directory if path includes subdirectories
    dir_path = os.path.dirname(save_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    with open(save_path, 'w') as f:
        f.write(html_content)
    
    print(f"✓ Created HTML dashboard: {save_path}")


if __name__ == "__main__":
    # Test
    import pandas as pd
    df = pd.read_csv('data/processed/merged_data_clean_weekly.csv')
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').sort_index()
    
    # Mock analysis results
    analysis_results = {
        'conditional': {'p_I_high': 0.619, 'p_I_low': 0.958},
        'statistical_tests': {'z_statistic': -5.3695, 'p_value': 0.000000}                                                                                      
    }
    
    source_urls = {
        'owid': 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv',
        'who': 'h                                                           ttps://srhdpeuwpubsa.blob.core.windows.net/whdh/COVID/WHO-COVID-19-global-data.csv',
        'nyt': 'https://raw.                                                                                                                                                                                                                                                              githubusercontent.com/nytimes/covid-19-data/master/us.csv'
    }                                                                                                                                                                                                           
    
    create_html_dashboard(df, analysis_results, source_urls)
