# COVID-19 Vaccination vs Infection Analysis

Statistical analysis project examining the relationship between vaccination rates and COVID-19 case counts using data from multiple sources.

## Overview

This project analyzes COVID-19 data from the United States (2020-2022) to investigate the relationship between vaccination rates and weekly new case counts. The analysis uses correlation analysis and demonstrates the importance of controlling for temporal confounding variables in epidemiological research.

## Data Sources

- **OWID (Our World in Data)**: Comprehensive COVID-19 dataset with vaccination data
- **WHO (World Health Organization)**: Global COVID-19 surveillance data
- **NY Times**: COVID-19 case and death data for the United States

All data sources are publicly available and automatically downloaded when running the analysis.

## Project Structure

```
Final Project Statistics/
├── src/
│   ├── extract_data.py      # Downloads data from all 3 sources
│   ├── process_data.py       # Cleans and aggregates data to weekly
│   ├── analyze.py            # Performs statistical analysis
│   └── generate_html.py      # Creates the HTML dashboard
├── data/
│   ├── raw/                  # Raw CSV files from data sources
│   └── processed/            # Clean weekly aggregated data
├── main.py                   # Main execution script
├── index.html                # Generated HTML dashboard
└── requirements.txt          # Python dependencies
```

## Installation

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the complete analysis pipeline:
```bash
python main.py
```

This will:
1. Download data from all 3 sources
2. Process and clean the data (aggregate to weekly)
3. Perform statistical analysis (correlation analysis)
4. Generate the HTML dashboard (`index.html`)

## Results

The analysis finds a significant positive correlation (r = 0.197, p = 0.014) between vaccination rates and weekly case counts. This result demonstrates temporal confounding, where higher vaccination periods coincided with more transmissible variants (Delta, Omicron), rather than indicating that vaccination increases transmission.

## Key Findings

- **Correlation Coefficient**: 0.197 (positive, weak-moderate)
- **Statistical Significance**: p = 0.014 (significant)
- **Interpretation**: The positive correlation reflects temporal confounding where vaccination rollout and variant emergence happened simultaneously, highlighting the importance of controlling for confounding variables in epidemiological analysis.

## Research Context

Published research (Au, 2022) that controls for temporal confounding factors finds that vaccination reduces transmission. Our simple correlation analysis demonstrates the exact temporal confounding effect that sophisticated statistical methods are designed to address.

## Requirements

- Python 3.7+
- pandas
- numpy
- scipy
- requests

See `requirements.txt` for complete list.

## License

This project uses publicly available data for educational/research purposes.

