"""
Data collection script for US-CPI-Forecasting.

This script downloads macroeconomic data from FRED and saves:
1. Raw monthly macro data
2. Processed monthly dataset for modeling
"""

from pathlib import Path
import pandas as pd
from pandas_datareader import data as web


START_DATE = "1990-01-01"
END_DATE = None

SERIES = {
    "CPI": "CPIAUCSL",
    "Core_CPI": "CPILFESL",
    "Fed_Funds_Rate": "FEDFUNDS",
    "Unemployment_Rate": "UNRATE",
    "PPI": "PPIACO",
    "Industrial_Production": "INDPRO",
    "Oil_Price_WTI": "WTISPLC",
    "Ten_Year_Treasury": "DGS10",
}


def download_fred_data(series_dict, start=START_DATE, end=END_DATE):
    df = web.DataReader(list(series_dict.values()), "fred", start, end)
    reverse_map = {v: k for k, v in series_dict.items()}
    df = df.rename(columns=reverse_map)
    df.index.name = "Date"
    return df


def process_monthly_data(df):
    monthly = df.resample("M").last()

    monthly["CPI_YoY"] = monthly["CPI"].pct_change(12) * 100
    monthly["Core_CPI_YoY"] = monthly["Core_CPI"].pct_change(12) * 100
    monthly["PPI_YoY"] = monthly["PPI"].pct_change(12) * 100
    monthly["Oil_YoY"] = monthly["Oil_Price_WTI"].pct_change(12) * 100
    monthly["Industrial_Production_YoY"] = monthly["Industrial_Production"].pct_change(12) * 100

    monthly["CPI_YoY_Next_Month"] = monthly["CPI_YoY"].shift(-1)

    monthly = monthly.dropna()
    return monthly


def main():
    base_dir = Path(__file__).resolve().parents[1]
    raw_dir = base_dir / "data" / "raw"
    processed_dir = base_dir / "data" / "processed"

    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    raw_df = download_fred_data(SERIES)
    processed_df = process_monthly_data(raw_df)

    raw_df.to_csv(raw_dir / "fred_raw_macro_data.csv")
    processed_df.to_csv(processed_dir / "monthly_modeling_dataset.csv")

    print("Data collection complete.")
    print(f"Raw data shape: {raw_df.shape}")
    print(f"Processed data shape: {processed_df.shape}")
    print("Saved to data/raw/ and data/processed/")


if __name__ == "__main__":
    main()
