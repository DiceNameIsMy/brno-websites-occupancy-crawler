#!/usr/bin/env python3
"""
Visualize Luzanky Pool Crowd Data

This script analyzes and visualizes crowd density data from a CSV file.
The expected data format is 'timestamp,occupancy', where occupancy is a string like '136/634'.
"""

import argparse
import logging
import sys

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants
DEFAULT_CSV_PATH = "data/luzanky.csv"
OUTPUT_FILENAME = "luzanky_plots.png"


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load and preprocess the CSV data.

    Args:
        file_path: Path to the CSV file.

    Returns:
        Processed DataFrame with 'timestamp', 'current', 'capacity', and 'occupancy_percent'.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error reading CSV: {e}")
        sys.exit(1)

    # Clean column names
    df.columns = df.columns.str.strip().str.lower()

    if "timestamp" not in df.columns or "occupancy" not in df.columns:
        logging.error("CSV must contain 'timestamp' and 'occupancy' columns.")
        sys.exit(1)

    # Parse timestamp
    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    except Exception as e:
        logging.error(f"Error parsing timestamps: {e}")
        sys.exit(1)

    # Parse occupancy "current/capacity"
    try:
        # Split 'occupancy' into 'current' and 'capacity'
        # Assumes format "123/456"
        split_data = df["occupancy"].str.split("/", expand=True)

        # Check if split resulted in 2 columns
        if split_data.shape[1] != 2:
            logging.warning(
                "Some occupancy rows do not match 'current/capacity' format. Filtering them out."
            )
            # We can valid rows by checking which are not None
            valid_rows = split_data[1].notna()
            split_data = split_data[valid_rows]
            df = df[valid_rows]

        df["current"] = pd.to_numeric(split_data[0])
        df["capacity"] = pd.to_numeric(split_data[1])

        # Calculate percentage
        # Handle division by zero if capacity is 0 (unlikely but safe)
        df["occupancy_percent"] = (df["current"] / df["capacity"]) * 100

    except Exception as e:
        logging.error(f"Error parsing occupancy column: {e}")
        sys.exit(1)

    return df


def analyze_data(df: pd.DataFrame) -> None:
    """
    Print summary statistics.

    Args:
        df: Processed DataFrame.
    """
    total_rows = len(df)
    if total_rows == 0:
        print("No data available for analysis.")
        return

    start_date = df["timestamp"].min()
    end_date = df["timestamp"].max()
    duration = end_date - start_date

    max_current = df["current"].max()
    avg_current = df["current"].mean()
    mean_percent = df["occupancy_percent"].mean()

    print("-" * 30)
    print("DATA SUMMARY")
    print("-" * 30)
    print(f"Total Observations: {total_rows}")
    print(f"Date Range: {start_date} to {end_date}")
    print(f"Duration: {duration}")
    print(f"Max Occupancy: {max_current}")
    print(f"Average Occupancy: {avg_current:.1f} people ({mean_percent:.1f}%)")
    print("-" * 30)

    # Busiest days
    df["day_name"] = df["timestamp"].dt.day_name()
    avg_by_day = df.groupby("day_name")["current"].mean().sort_values(ascending=False)

    print("\nAVERAGE OCCUPANCY BY DAY")
    print("-" * 30)
    print(avg_by_day)
    print("-" * 30)


def visualize_data(df: pd.DataFrame, output_file: str) -> None:
    """
    Generate and save visualization plots.

    Args:
        df: Processed DataFrame.
        output_file: Path to save the plot image.
    """
    if df.empty:
        logging.warning("No data to visualize.")
        return

    sns.set_theme(style="whitegrid")

    # Layout:
    # 2 Rows:
    # Top: Time Series of People Count
    # Bottom: Heatmap of Average Count by Day/Hour
    fig = plt.figure(figsize=(12, 10), constrained_layout=True)
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 1])

    ax_ts = fig.add_subplot(gs[0])
    ax_heatmap = fig.add_subplot(gs[1])

    # --- 1. Time Series Plot ---
    sns.lineplot(
        data=df, x="timestamp", y="current", ax=ax_ts, linewidth=1.5, color="royalblue"
    )

    ax_ts.set_title("Pool Utilization Over Time", fontsize=14)
    ax_ts.set_ylabel("Number of People")
    ax_ts.set_xlabel("Date")

    # Format X axis dates
    ax_ts.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax_ts.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.setp(ax_ts.get_xticklabels(), rotation=45, ha="right")

    # Add capacity line if constant or use max capacity found
    max_cap = df["capacity"].max()
    ax_ts.axhline(
        y=max_cap,
        color="red",
        linestyle="--",
        alpha=0.5,
        label=f"Max Capacity ({max_cap})",
    )
    ax_ts.legend(loc="upper right")
    ax_ts.grid(True, which="both", linestyle="--", linewidth=0.5)

    # --- 2. Heatmap (Day vs Hour) ---
    days_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    df["hour"] = df["timestamp"].dt.hour
    df["day_name"] = df["timestamp"].dt.day_name()

    heatmap_data = df.groupby(["day_name", "hour"])["current"].mean().reset_index()

    pivot_df = heatmap_data.pivot(index="day_name", columns="hour", values="current")
    pivot_df = pivot_df.reindex(days_order)

    # Determine sensible max for heatmap color scale (e.g., max observed average or capacity)
    # Using 95th percentile of actual data for better contrast, or just max value
    vmax_val = heatmap_data["current"].max()

    sns.heatmap(
        pivot_df,
        cmap="YlOrRd",  # Yellow to Red
        annot=True,  # Show values
        fmt=".0f",  # Integers
        linewidths=0.5,
        vmin=0,
        vmax=vmax_val,
        ax=ax_heatmap,
        cbar_kws={"label": "Avg People Count"},
    )

    ax_heatmap.set_title("Average Crowdedness: Day vs Hour", fontsize=14)
    ax_heatmap.set_ylabel("")
    ax_heatmap.set_xlabel("Hour of Day")

    # Save
    try:
        plt.savefig(output_file, dpi=150)
        logging.info(f"Plots saved to {output_file}")
    except Exception as e:
        logging.error(f"Error saving plot: {e}")


def main():
    parser = argparse.ArgumentParser(description="Visualize Luzanky Pool Crowd Data")
    parser.add_argument(
        "--file",
        type=str,
        default=DEFAULT_CSV_PATH,
        help=f"Path to CSV file (default: {DEFAULT_CSV_PATH})",
    )
    args = parser.parse_args()

    logging.info(f"Loading data from {args.file}...")
    df = load_data(args.file)

    logging.info("Analyzing data...")
    analyze_data(df)

    logging.info(f"Generating visualizations to {OUTPUT_FILENAME}...")
    visualize_data(df, OUTPUT_FILENAME)

    logging.info("Done.")


if __name__ == "__main__":
    main()
