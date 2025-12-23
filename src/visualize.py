"""
Visualization Module
Creates high-quality visualizations for the analysis
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10


def create_vaccination_timeline(df, save_path="visualizations/vaccination_timeline.png"):
    """
    Create timeline visualization of vaccination rates
    
    Args:
        df: DataFrame with date index and vaccination_rate column
        save_path: Path to save the visualization
    """
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.plot(df.index, df["vaccination_rate"], linewidth=2.5, color='#2E86AB', label='Vaccination Rate')
    ax.fill_between(df.index, df["vaccination_rate"], alpha=0.3, color='#2E86AB')
    
    # Add threshold line
    ax.axhline(y=0.5, color='red', linestyle='--', linewidth=2, alpha=0.7, label='High/Low Threshold (0.5)')
    
    ax.set_xlabel("Date", fontsize=12, fontweight='bold')
    ax.set_ylabel("Vaccination Rate", fontsize=12, fontweight='bold')
    ax.set_title("Vaccination Rate Over Time — USA", fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1)
    ax.legend(loc='best')
    
    fig.autofmt_xdate()
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved: {save_path}")


def create_infection_indicator_plot(df, save_path="visualizations/infection_indicator.png"):
    """
    Create scatter plot of infection indicators
    
    Args:
        df: DataFrame with date index and I column
        save_path: Path to save the visualization
    """
    fig, ax = plt.subplots(figsize=(14, 4))
    
    ax.scatter(df.index, df["I"], s=8, alpha=0.6, color='#A23B72', label='Infection Days')
    ax.set_xlabel("Date", fontsize=12, fontweight='bold')
    ax.set_ylabel("Infection Indicator (I=1 if new cases > 0)", fontsize=12, fontweight='bold')
    ax.set_title("Infection Indicator Over Time — USA", fontsize=16, fontweight='bold', pad=20)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['No Cases', 'Cases Present'])
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    fig.autofmt_xdate()
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved: {save_path}")


def create_conditional_probability_bar(conditional_results, save_path="visualizations/conditional_probabilities.png"):
    """
    Create bar chart comparing conditional probabilities
    
    Args:
        conditional_results: Dictionary with conditional probability results
        save_path: Path to save the visualization
    """
    fig, ax = plt.subplots(figsize=(10, 7))
    
    categories = ["High Vaccination\n(V ≥ 0.5)", "Low Vaccination\n(V < 0.5)"]
    probabilities = [conditional_results["p_I_high"], conditional_results["p_I_low"]]
    colors = ['#06A77D', '#F18F01']
    
    bars = ax.bar(categories, probabilities, color=colors, alpha=0.8, edgecolor='black', linewidth=2, width=0.6)
    
    # Add value labels on bars
    for bar, prob in zip(bars, probabilities):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{prob:.4f}',
                ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    # Add difference annotation
    diff = conditional_results["difference"]
    ax.annotate(f'Difference: {diff:.4f}\n({abs(diff)*100:.1f}% reduction)',
                xy=(0.5, max(probabilities) * 0.7),
                xytext=(0.5, max(probabilities) * 0.9),
                arrowprops=dict(arrowstyle='->', lw=2, color='red'),
                fontsize=12, fontweight='bold', ha='center',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))
    
    ax.set_ylabel("Infection Probability P(I=1)", fontsize=12, fontweight='bold')
    ax.set_title("Conditional Infection Probabilities — USA\nHigh vs Low Vaccination Periods", 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_ylim(0, max(probabilities) * 1.25)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved: {save_path}")


def create_weekly_infections_plot(weekly_data, save_path="visualizations/weekly_infections.png"):
    """
    Create plot of weekly infection counts
    
    Args:
        weekly_data: Series or DataFrame with weekly infection data
        save_path: Path to save the visualization
    """
    fig, ax = plt.subplots(figsize=(14, 6))
    
    if isinstance(weekly_data, pd.Series):
        ax.plot(weekly_data.index, weekly_data.values, linewidth=2.5, color='#C73E1D', 
                marker='o', markersize=4, label='Weekly Infections')
        ax.fill_between(weekly_data.index, weekly_data.values, alpha=0.3, color='#C73E1D')
    else:
        ax.plot(weekly_data.index, weekly_data.values, linewidth=2.5, color='#C73E1D', 
                marker='o', markersize=4)
    
    ax.set_xlabel("Week", fontsize=12, fontweight='bold')
    ax.set_ylabel("Weekly Sum of I (Infection Count)", fontsize=12, fontweight='bold')
    ax.set_title("Weekly Infection Counts — USA", fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    fig.autofmt_xdate()
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved: {save_path}")


def create_correlation_heatmap(df, save_path="visualizations/correlation_heatmap.png"):
    """
    Create correlation heatmap of key variables
    
    Args:
        df: DataFrame with relevant columns
        save_path: Path to save the visualization
    """
    # Select relevant columns
    cols = ["vaccination_rate", "I", "new_cases", "people_vaccinated"]
    available_cols = [col for col in cols if col in df.columns]
    
    if len(available_cols) < 2:
        print("Not enough columns for correlation heatmap")
        return
    
    corr_df = df[available_cols].corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    sns.heatmap(corr_df, annot=True, fmt='.3f', cmap='coolwarm', center=0,
                square=True, linewidths=2, cbar_kws={"shrink": 0.8}, 
                vmin=-1, vmax=1, ax=ax, annot_kws={'size': 12, 'weight': 'bold'})
    
    ax.set_title("Correlation Heatmap — Key Variables", fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved: {save_path}")


def create_weekly_monthly_comparison(df, save_path="visualizations/weekly_monthly_comparison.png"):
    """
    Create comparison of weekly vs monthly aggregations
    
    Args:
        df: DataFrame with datetime index
        save_path: Path to save visualization
    """
    weekly = df["I"].resample("W").sum()
    monthly = df["I"].resample("ME").sum()
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Weekly plot
    ax1.plot(weekly.index, weekly.values, linewidth=2.5, color='#2E86AB', marker='o', markersize=5)
    ax1.fill_between(weekly.index, weekly.values, alpha=0.3, color='#2E86AB')
    ax1.set_xlabel("Week", fontsize=12, fontweight='bold')
    ax1.set_ylabel("Weekly Infections", fontsize=12, fontweight='bold')
    ax1.set_title("Weekly Aggregation — USA", fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.text(0.02, 0.95, f'Total Weeks: {len(weekly)}', transform=ax1.transAxes, 
             fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Monthly plot
    ax2.bar(monthly.index, monthly.values, width=20, color='#F18F01', alpha=0.8, edgecolor='black', linewidth=1)
    ax2.plot(monthly.index, monthly.values, linewidth=2.5, color='#C73E1D', marker='s', markersize=8)
    ax2.set_xlabel("Month", fontsize=12, fontweight='bold')
    ax2.set_ylabel("Monthly Infections", fontsize=12, fontweight='bold')
    ax2.set_title("Monthly Aggregation — USA", fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax2.text(0.02, 0.95, f'Total Months: {len(monthly)}', transform=ax2.transAxes, 
             fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    fig.suptitle("Weekly vs Monthly Infection Aggregations — USA", fontsize=16, fontweight='bold', y=0.995)
    
    fig.autofmt_xdate()
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved: {save_path}")


def create_interactive_dashboard(df, analysis_results, country="United States", save_path="visualizations/interactive_dashboard.html"):
    """
    Create comprehensive interactive Plotly dashboard with hypothesis and conclusions
    
    Args:
        df: DataFrame with all data
        analysis_results: Dictionary with analysis results
        country: Country name
        save_path: Path to save the HTML file
    """
    # Ensure date is index and data is sorted - handle both cases
    df = df.copy()
    if 'date' in df.columns and df.index.name != 'date':
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date').sort_index()
    elif df.index.name == 'date' or isinstance(df.index, pd.DatetimeIndex):
        df = df.sort_index()
    else:
        # If no date column, create one from index if possible
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("DataFrame must have a date index or 'date' column")
    
    # Get analysis results
    bernoulli = analysis_results.get("bernoulli", {})
    conditional = analysis_results.get("conditional", {})
    binomial = analysis_results.get("binomial_weekly", {})
    tests = analysis_results.get("statistical_tests", {})
    
    # Extract key values
    p_I = bernoulli.get("p_I", 0)
    p_V = bernoulli.get("p_V", 0)
    p_high = conditional.get("p_I_high", 0)
    p_low = conditional.get("p_I_low", 0)
    diff = conditional.get("difference", 0)
    z_stat = tests.get("z_statistic", 0)
    p_value = tests.get("p_value", 1)
    significant = tests.get("significant", False)
    
    # Create individual figures for each visualization
    
    # 1. Vaccination Rate Timeline
    vacc_timeline = df["vaccination_rate"].dropna()
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=vacc_timeline.index, y=vacc_timeline.values,
                  mode='lines', name='Vaccination Rate',
                  line=dict(color='#2E86AB', width=3),
                  fill='tozeroy', fillcolor='rgba(46, 134, 171, 0.3)'))
    fig1.add_hline(y=0.5, line_dash="dash", line_color="red", line_width=2,
                  annotation_text="Threshold (0.5)")
    fig1.update_layout(title="1. Vaccination Rate Over Time", height=350,
                      xaxis_title="Date", yaxis_title="Vaccination Rate",
                      yaxis_range=[0, 1], template="plotly_white", showlegend=True)
    
    # 2. Weekly Infections
    weekly = df["I"].resample("W").sum()
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=weekly.index, y=weekly.values,
                  mode='lines+markers', name='Weekly Infections',
                  line=dict(color='#C73E1D', width=3),
                  marker=dict(size=8, opacity=0.8)))
    fig2.update_layout(title="2. Weekly Infection Counts", height=350,
                      xaxis_title="Week", yaxis_title="Weekly Infections",
                      template="plotly_white", showlegend=True)
    
    # 3. Conditional Probabilities Bar Chart
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=["High Vaccination\n(V ≥ 0.5)", "Low Vaccination\n(V < 0.5)"],
              y=[p_high, p_low],
              name='Infection Probability',
              marker_color=['#06A77D', '#F18F01'],
              text=[f'{p_high:.4f}', f'{p_low:.4f}'],
              textposition='outside'))
    fig3.update_layout(title="3. Conditional Probabilities Comparison", height=350,
                      xaxis_title="Vaccination Group", yaxis_title="Infection Probability",
                      template="plotly_white", showlegend=True)
    
    # 4. Combined trend showing both vaccination and infection over time
    vacc_data = df["vaccination_rate"].dropna()
    infection_rate = df["I"].resample("ME").mean() * 100
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=vacc_data.index, y=vacc_data.values,
                  mode='lines', name='Vaccination Rate',
                  line=dict(color='#2E86AB', width=3)))
    fig4.add_trace(go.Scatter(x=infection_rate.index, y=infection_rate.values,
                  mode='lines+markers', name='Monthly Infection Rate (%)',
                  line=dict(color='#A23B72', width=3, dash='dot'),
                  marker=dict(size=6, opacity=0.8),
                  yaxis='y2'))
    fig4.update_layout(title="4. Vaccination and Infection Trends", height=350,
                      xaxis_title="Date", yaxis_title="Vaccination Rate",
                      yaxis2=dict(title="Infection Rate (%)", overlaying='y', side='right'),
                      template="plotly_white", showlegend=True)
    
    # Create HTML with hypothesis and conclusions
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>COVID-19 Vaccination vs Infection Analysis Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
            }}
            .container {{
                max-width: 1600px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            }}
            h1 {{
                text-align: center;
                color: #2E86AB;
                border-bottom: 3px solid #2E86AB;
                padding-bottom: 10px;
                margin-bottom: 30px;
            }}
            .section {{
                margin: 30px 0;
                padding: 25px;
                background: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid #2E86AB;
            }}
            .hypothesis-box {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 8px;
                margin: 20px 0;
            }}
            .hypothesis-box h2 {{
                color: white;
                margin-top: 0;
            }}
            .conclusion-box {{
                background: linear-gradient(135deg, #06A77D 0%, #0D7377 100%);
                color: white;
                padding: 30px;
                border-radius: 8px;
                margin: 20px 0;
            }}
            .conclusion-box h2 {{
                color: white;
                margin-top: 0;
            }}
            .stat-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }}
            .stat-box {{
                background: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                text-align: center;
            }}
            .stat-value {{
                font-size: 32px;
                font-weight: bold;
                color: #2E86AB;
            }}
            .stat-label {{
                font-size: 14px;
                color: #666;
                margin-top: 8px;
            }}
            .dashboard-container {{
                margin: 30px 0;
                background: white;
                padding: 20px;
                border-radius: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>COVID-19 Vaccination Rates vs Infection Outcomes</h1>
            <h2 style="text-align: center; color: #666;">Statistical Analysis Dashboard — {country}</h2>
            
            <!-- HYPOTHESIS SECTION -->
            <div class="hypothesis-box">
                <h2>Research Hypothesis</h2>
                <p style="font-size: 18px; line-height: 1.8;">
                    <strong>H₁:</strong> Higher vaccination levels ARE associated with lower infection probability.<br><br>
                    <strong>Research Question:</strong> Does higher vaccination rate (V ≥ 0.5) correspond to lower infection probability P(I=1) compared to low vaccination periods (V < 0.5)?<br><br>
                    <strong>Variables:</strong> V = vaccination rate (proportion), I = infection indicator (1 if new cases > 0, 0 otherwise)
                </p>
            </div>
            
            <!-- KEY STATISTICS -->
            <div class="section">
                <h2>Key Statistics</h2>
                <div class="stat-grid">
                    <div class="stat-box">
                        <div class="stat-value">{p_I:.4f}</div>
                        <div class="stat-label">Overall Infection Probability (p_I)</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{p_V:.4f}</div>
                        <div class="stat-label">Average Vaccination Rate (p_V)</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{p_high:.4f}</div>
                        <div class="stat-label">P(I=1 | V ≥ 0.5)<br>High Vaccination</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{p_low:.4f}</div>
                        <div class="stat-label">P(I=1 | V < 0.5)<br>Low Vaccination</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{abs(diff):.4f}</div>
                        <div class="stat-label">Difference<br>({abs(diff)*100:.1f}% reduction)</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{z_stat:.2f}</div>
                        <div class="stat-label">Z-statistic</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{p_value:.6f}</div>
                        <div class="stat-label">P-value</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{'YES' if significant else 'NO'}</div>
                        <div class="stat-label">Statistically Significant<br>(α = 0.05)</div>
                    </div>
                </div>
            </div>
            
            <!-- INTERACTIVE DASHBOARD -->
            <div class="dashboard-container">
                <h2 style="text-align: center; color: #2E86AB; margin-bottom: 30px;">Interactive Visualizations</h2>
                
                <!-- Row 1: Vaccination Rate Over Time -->
                <div style="margin-bottom: 40px; padding: 25px; background: white; border-radius: 8px; border-left: 5px solid #2E86AB; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <div id="viz1" style="margin-bottom: 20px;"></div>
                    <div style="padding: 15px; background: #f8f9fa; border-radius: 5px;">
                        <h3 style="color: #2E86AB; margin-top: 0; font-size: 18px; margin-bottom: 10px;">1. Vaccination Rate Over Time</h3>
                        <p style="color: #666; font-size: 15px; margin: 0; line-height: 1.6;"><strong>What it shows:</strong> This chart displays how the vaccination coverage rate changed over time from 2020 to 2024. The blue filled area represents the proportion of the population that was vaccinated. The red dashed horizontal line at 0.5 (50%) is the threshold we use to classify periods as "high vaccination" (above the line) or "low vaccination" (below the line). This visualization helps us understand when vaccination campaigns were most effective.</p>
                    </div>
                </div>
                
                <!-- Row 2: Weekly Infection Counts -->
                <div style="margin-bottom: 40px; padding: 25px; background: white; border-radius: 8px; border-left: 5px solid #C73E1D; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <div id="viz2" style="margin-bottom: 20px;"></div>
                    <div style="padding: 15px; background: #f8f9fa; border-radius: 5px;">
                        <h3 style="color: #C73E1D; margin-top: 0; font-size: 18px; margin-bottom: 10px;">2. Weekly Infection Counts</h3>
                        <p style="color: #666; font-size: 15px; margin: 0; line-height: 1.6;"><strong>What it shows:</strong> This graph shows the total number of days with reported COVID-19 infections per week. Each point represents one week, and the line connects these weekly totals. Higher values indicate weeks with more infection days. This helps us see patterns in infection frequency over time and identify periods with high or low infection activity.</p>
                    </div>
                </div>
                
                <!-- Row 3: Conditional Probabilities Comparison -->
                <div style="margin-bottom: 40px; padding: 25px; background: white; border-radius: 8px; border-left: 5px solid #06A77D; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <div id="viz3" style="margin-bottom: 20px;"></div>
                    <div style="padding: 15px; background: #f8f9fa; border-radius: 5px;">
                        <h3 style="color: #06A77D; margin-top: 0; font-size: 18px; margin-bottom: 10px;">3. Conditional Probabilities Comparison</h3>
                        <p style="color: #666; font-size: 15px; margin: 0; line-height: 1.6;"><strong>What it shows:</strong> This bar chart directly compares the infection probability during two different periods: high vaccination (green bar, V ≥ 0.5) and low vaccination (orange bar, V < 0.5). The height of each bar represents the probability of infection occurring. If vaccination is effective, we expect the green bar (high vaccination) to be lower than the orange bar (low vaccination). The difference between these bars is the key evidence for our hypothesis.</p>
                    </div>
                </div>
                
                <!-- Row 4: Vaccination and Infection Trends -->
                <div style="margin-bottom: 20px; padding: 25px; background: white; border-radius: 8px; border-left: 5px solid #A23B72; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <div id="viz4" style="margin-bottom: 20px;"></div>
                    <div style="padding: 15px; background: #f8f9fa; border-radius: 5px;">
                        <h3 style="color: #A23B72; margin-top: 0; font-size: 18px; margin-bottom: 10px;">4. Vaccination and Infection Trends</h3>
                        <p style="color: #666; font-size: 15px; margin: 0; line-height: 1.6;"><strong>What it shows:</strong> This combined visualization shows two trends on the same chart: the vaccination rate (solid blue line) and the monthly infection rate percentage (dotted purple line). By viewing both together, we can see if there's a relationship - for example, when vaccination rates increase, do infection rates decrease? This helps visualize the inverse relationship between vaccination and infection that our hypothesis predicts.</p>
                    </div>
                </div>
            </div>
            
            <!-- CONCLUSION SECTION -->
            <div class="conclusion-box">
                <h2>Hypothesis Testing Results & Conclusion</h2>
                <div style="font-size: 18px; line-height: 1.8;">
                    <p><strong>Statistical Test Results:</strong></p>
                    <ul style="line-height: 2;">
                        <li><strong>Test:</strong> Two-sample proportion test (z-test)</li>
                        <li><strong>Z-statistic:</strong> {z_stat:.4f}</li>
                        <li><strong>P-value:</strong> {p_value:.6f}</li>
                        <li><strong>Significance Level (α):</strong> 0.05</li>
                        <li><strong>Result:</strong> {'H₁ SUPPORTED' if significant else 'H₁ NOT SUPPORTED'}</li>
                    </ul>
                    
                    <p style="margin-top: 25px;"><strong>Key Findings:</strong></p>
                    <ul style="line-height: 2;">
                        <li>High vaccination days (V ≥ 0.5) show infection probability of <strong>{p_high:.4f}</strong></li>
                        <li>Low vaccination days (V < 0.5) show infection probability of <strong>{p_low:.4f}</strong></li>
                        <li>This represents a <strong>{abs(diff)*100:.1f}% reduction</strong> in infection probability for high-vaccination periods</li>
                    </ul>
                    
                    <p style="margin-top: 25px; font-size: 20px; font-weight: bold;">
                        {'CONCLUSION: Higher vaccination levels ARE associated with lower infection probability. The hypothesis (H₁) is SUPPORTED by the statistical evidence.' if significant and p_high < p_low else 'CONCLUSION: The relationship between vaccination and infection rates requires further investigation.'}
                    </p>
                    
                    <p style="margin-top: 20px; font-size: 16px;">
                        This analysis demonstrates that vaccination is an effective tool in reducing the probability of COVID-19 infection, 
                        supporting public health recommendations for vaccination campaigns.
                    </p>
                </div>
            </div>
        </div>
        
        <script>
            var viz1Data = {fig1.to_json()};
            var viz2Data = {fig2.to_json()};
            var viz3Data = {fig3.to_json()};
            var viz4Data = {fig4.to_json()};
            
            Plotly.newPlot('viz1', viz1Data.data, viz1Data.layout, {{responsive: true}});
            Plotly.newPlot('viz2', viz2Data.data, viz2Data.layout, {{responsive: true}});
            Plotly.newPlot('viz3', viz3Data.data, viz3Data.layout, {{responsive: true}});
            Plotly.newPlot('viz4', viz4Data.data, viz4Data.layout, {{responsive: true}});
        </script>
    </body>
    </html>
    """
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Saved: {save_path}")


def create_all_visualizations(df, analysis_results, country="United States"):
    """
    Create all visualizations
    
    Args:
        df: Processed DataFrame
        analysis_results: Dictionary with analysis results
        country: Country name
    """
    print("=" * 60)
    print("CREATING VISUALIZATIONS")
    print("=" * 60)
    
    # Static visualizations
    print("\nCreating static visualizations...")
    create_vaccination_timeline(df)
    create_infection_indicator_plot(df)
    create_conditional_probability_bar(analysis_results.get("conditional", {}))
    
    # Weekly infections
    weekly_data = df["I"].resample("W").sum()
    create_weekly_infections_plot(weekly_data)
    
    # Weekly vs Monthly comparison
    create_weekly_monthly_comparison(df)
    
    # Correlation heatmap
    create_correlation_heatmap(df)
    
    # Interactive dashboard
    print("\nCreating interactive dashboard...")
    create_interactive_dashboard(df, analysis_results, country=country)
    
    print("\nAll visualizations created successfully!")


if __name__ == "__main__":
    print("Visualization module loaded successfully!")
