#!/usr/bin/env python3
"""
Visualize Hangar Crowd Data

This script analyzes and visualizes crowd density data from a CSV file.
It generates a time-series plot of crowd levels and aggregated plots
showing average occupancy by hour of the day and day of the week.
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
DEFAULT_CSV_PATH = "data/hangar.csv"
OUTPUT_FILENAME = "hangar_plots.png"

# Mapping of occupancy text to numerical levels
OCCUPANCY_MAPPING = {
    "Closed for now – check out the opening hours in the Contacts section.": 0,
    "Open! Plenty of space, hardly anyone around – all yours.": 1,
    "Open! You won’t be lonely – a nice, balanced crowd.": 2,
    "The Hangar is buzzing! Full-on bouldering vibes, expect a bit of a squeeze.": 3,
}

# Reverse mapping for labels
LEVEL_LABELS = {
    0: "Closed",
    1: "Plenty of Space",
    2: "Balanced Crowd",
    3: "Buzzing / Full",
}


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load and preprocess the CSV data.

    Args:
        file_path: Path to the CSV file.

    Returns:
        Processed DataFrame with 'timestamp' and 'occupancy_level'.
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

    # Map occupancy to levels
    df["occupancy_level"] = df["occupancy"].map(OCCUPANCY_MAPPING)

    # Check for unmapped values
    unknown_states = df[df["occupancy_level"].isna()]["occupancy"].unique()
    if len(unknown_states) > 0:
        logging.warning(f"Found unknown occupancy states: {unknown_states}")
        # Drop unknown states for plotting stability
        df = df.dropna(subset=["occupancy_level"])

    # Cast to integer after dropping NaNs
    df["occupancy_level"] = df["occupancy_level"].astype(int)

    return df


def analyze_data(df: pd.DataFrame) -> None:
    """
    Print summary statistics and optimal visiting times.

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

    print("-" * 30)
    print("DATA SUMMARY")
    print("-" * 30)
    print(f"Total Observations: {total_rows}")
    print(f"Date Range: {start_date} to {end_date}")
    print(f"Duration: {duration}")
    print("-" * 30)

    # --- Heatmap Preparation ---
    open_only_df = df[df["occupancy_level"] > 0].copy()

    # Counts by day for availability plot
    # Use all data to show crawler health/frequency
    df["day_name"] = df["timestamp"].dt.day_name()
    days_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    # --- Print Stats ---
    print("\nDATA AVAILABILITY (Counts per Day)")
    print("-" * 30)
    # Reindex to ensure all days show up even if 0
    counts = df["day_name"].value_counts().reindex(days_order, fill_value=0)
    print(counts)
    print("-" * 30)

    if not open_only_df.empty:
        open_only_df["hour"] = open_only_df["timestamp"].dt.hour
        open_only_df["day_name"] = open_only_df["timestamp"].dt.day_name()

        # Aggregate for Heatmap
        heatmap_data = (
            open_only_df.groupby(["day_name", "hour"])["occupancy_level"]
            .mean()
            .reset_index()
        )

        # Pivot: Rows=Day of Week, Cols=Hour
        heatmap_pivot = heatmap_data.pivot(
            index="day_name", columns="hour", values="occupancy_level"
        )

        # Reindex rows to sorted days
        heatmap_pivot = heatmap_pivot.reindex(days_order)
    else:
        heatmap_pivot = pd.DataFrame()


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
    # Top Row: Time Series (Left), Counts (Right)
    # Bottom Row: Heatmap (Full Width)
    fig = plt.figure(figsize=(15, 12), constrained_layout=True)
    gs = fig.add_gridspec(2, 4)

    ax_ts = fig.add_subplot(gs[0, :3])  # Time series takes 3/4 width
    ax_counts = fig.add_subplot(gs[0, 3])  # Counts takes 1/4 width
    ax_heatmap = fig.add_subplot(gs[1, :])  # Heatmap takes full width

    # --- 1. Time Series Plot ---
    # Colors: 0: Gray, 1: Green, 2: Orange, 3: Red
    colors = {0: "gray", 1: "green", 2: "orange", 3: "red"}

    sns.scatterplot(
        data=df,
        x="timestamp",
        y="occupancy_level",
        hue="occupancy_level",
        palette=colors,
        ax=ax_ts,
        s=25,
        legend=True,
    )

    ax_ts.set_title("Occupancy Over Time", fontsize=14)
    ax_ts.set_ylabel("Level")
    ax_ts.set_xlabel("Date")
    ax_ts.set_yticks(list(LEVEL_LABELS.keys()))
    ax_ts.set_yticklabels([LEVEL_LABELS[k] for k in LEVEL_LABELS])
    ax_ts.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax_ts.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.setp(ax_ts.get_xticklabels(), rotation=45, ha="right")
    ax_ts.grid(True, which="both", linestyle="--", linewidth=0.5)

    # Adjust legend
    handles, labels = ax_ts.get_legend_handles_labels()
    # Map numeric labels to text
    labels = [LEVEL_LABELS.get(int(float(lbl)), lbl) for lbl in labels]
    ax_ts.legend(
        handles, labels, title="Status", loc="upper left", bbox_to_anchor=(1, 1)
    )

    # --- 2. Data Availability (Counts) ---
    days_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    # Ensure column exists
    if "day_name" not in df.columns:
        df["day_name"] = df["timestamp"].dt.day_name()

    sns.countplot(
        data=df,
        x="day_name",
        order=days_order,
        color="lightgray",
        edgecolor="black",
        ax=ax_counts,
    )
    ax_counts.set_title("Data Points", fontsize=14)
    ax_counts.set_xlabel("")
    ax_counts.set_ylabel("Count")
    plt.setp(ax_counts.get_xticklabels(), rotation=90)  # Vertical for space

    # --- 3. Heatmap (Day vs Hour) ---
    # Re-calculate heatmap pivot locally or pass it.
    # Better to recalculate clearly here for "Open" times.
    open_only_df = df[df["occupancy_level"] > 0].copy()

    if not open_only_df.empty:
        open_only_df["hour"] = open_only_df["timestamp"].dt.hour
        open_only_df["day_name"] = open_only_df["timestamp"].dt.day_name()

        heatmap_data = (
            open_only_df.groupby(["day_name", "hour"])["occupancy_level"]
            .mean()
            .reset_index()
        )

        pivot_df = heatmap_data.pivot(
            index="day_name", columns="hour", values="occupancy_level"
        )
        pivot_df = pivot_df.reindex(days_order)

        # Plot Heatmap
        sns.heatmap(
            pivot_df,
            cmap="RdYlGn_r",  # Red-Yellow-Green reversed
            annot=True,  # Show values
            fmt=".1f",  # 1 decimal place
            linewidths=0.5,
            vmin=1,
            vmax=3,  # Scale from 1 (Empty) to 3 (Full)
            ax=ax_heatmap,
            cbar_kws={"label": "Avg Occupancy (1=Low, 3=High)"},
        )
        title_heatmap = "Average Crowd Level: Day vs Hour (Green is Best)"
        ax_heatmap.set_title(title_heatmap, fontsize=16)
        ax_heatmap.set_ylabel("")
        ax_heatmap.set_xlabel("Hour of Day")
    else:
        ax_heatmap.text(
            0.5,
            0.5,
            "No 'Open' Data Available for Heatmap",
            ha="center",
            va="center",
            fontsize=12,
        )

    # Save
    try:
        plt.savefig(output_file, dpi=150)
        logging.info(f"Plots saved to {output_file}")

    except Exception as e:
        logging.error(f"Error saving plot: {e}")

    # Show (optional, if running interactively locally, but better to just save for headless envs)
    # plt.show()


def main():
    parser = argparse.ArgumentParser(description="Visualize Hangar Crowd Data")
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
