import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
from nsepython2 import fnolist, equity_history
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)


# Shared helper: fetch and clean data
def fetch_and_clean_data(stock, start_date, end_date):
    try:
        data = equity_history(stock, "EQ", start_date, end_date)
        if data is None or data.empty:
            print(f"No data returned for {stock}. Skipping.")
            return None
        # Convert relevant columns to numeric
        cols_to_numeric = [
            "CH_CLOSING_PRICE",
            "CH_PREVIOUS_CLS_PRICE",
            "CH_TRADE_HIGH_PRICE",
            "CH_TRADE_LOW_PRICE",
        ]
        for col in cols_to_numeric:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors="coerce")
        # Drop rows with NaN in any of the required columns
        data.dropna(subset=["CH_PREVIOUS_CLS_PRICE"], inplace=True)
        data = data[data["CH_PREVIOUS_CLS_PRICE"] > 0]
        if data.empty:
            print(f"Not enough valid data for {stock} after cleaning. Skipping.")
            return None
        return data
    except Exception as e:
        print(f"Error fetching/cleaning data for {stock}: {e}")
        return None


# Shared helper: plot histogram
def plot_volatility_histogram(data, col, stock, output_path, title):
    if col not in data.columns or data[col].dropna().empty:
        print(f"No '{col}' values to plot for {stock}. Skipping.")
        return

    plt.figure(figsize=(12, 7))

    # Calculate statistics
    mean_val = data[col].mean()
    std_val = data[col].std()
    median_val = data[col].median()
    min_val = data[col].min()
    max_val = data[col].max()

    # Calculate number of standard deviations needed on each side
    n_std_left = abs(int((min_val - mean_val) / std_val)) + 1
    n_std_right = abs(int((max_val - mean_val) / std_val)) + 1

    # Create bins centered on mean, with width = 1 standard deviation
    bins = [mean_val + (i * std_val) for i in range(-n_std_left, n_std_right + 1)]

    # Plot histogram
    plt.hist(data[col], bins=bins, edgecolor="black", alpha=0.75, color="deepskyblue")

    # Set x-axis ticks at each standard deviation
    xticks = [mean_val + (i * std_val) for i in range(-n_std_left, n_std_right + 1)]
    xtick_labels = [f"{x:.1f}" for x in xticks]
    plt.xticks(xticks, xtick_labels, rotation=45)

    # Add grid for better readability
    plt.grid(axis="both", linestyle=":", alpha=0.6)

    # Labels and title
    plt.title(title, fontsize=15, fontweight="bold")
    plt.xlabel(col, fontsize=13)
    plt.ylabel("Frequency", fontsize=13)

    # Stats box
    stats_text = (
        f"Mean: {mean_val:.4f}\nStd Dev: {std_val:.4f}\nMedian: {median_val:.4f}"
    )
    plt.text(
        0.05,
        0.95,
        stats_text,
        transform=plt.gca().transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.5", fc="wheat", alpha=0.5),
    )

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    try:
        plt.savefig(output_path)
        print(f"Histogram saved as {output_path}")
    except Exception as e:
        print(f"Error saving histogram for {stock} to {output_path}: {e}")
    plt.close()


def calculate_and_plot_daily_volatility(
    data, stock, api_one_year_ago_str, api_today_str, output_base_dir, date_folder_name
):
    output_directory = os.path.join(output_base_dir, date_folder_name, "daily_vix")
    os.makedirs(output_directory, exist_ok=True)

    print(f"\nProcessing daily volatility for stock: {stock}")

    # Calculate daily volatility (dv)
    if not all(
        col in data.columns for col in ["CH_CLOSING_PRICE", "CH_PREVIOUS_CLS_PRICE"]
    ):
        print(f"Missing required columns for {stock}. Skipping daily volatility.")
        return

    data["dv"] = (
        (data["CH_CLOSING_PRICE"] - data["CH_PREVIOUS_CLS_PRICE"])
        / data["CH_PREVIOUS_CLS_PRICE"]
    ) * 100
    data.dropna(subset=["dv"], inplace=True)
    if data["dv"].empty:
        print(f"No 'dv' values to plot for {stock} after calculation. Skipping.")
        return

    safe_stock_name = "".join(c if c.isalnum() else "_" for c in stock)
    image_filename = f"{safe_stock_name}_daily_vix.png"
    output_filepath = os.path.join(output_directory, image_filename)
    plot_volatility_histogram(
        data,
        "dv",
        stock,
        output_filepath,
        f"Daily Volatility (dv) Histogram for {stock}\nData: {api_one_year_ago_str} to {api_today_str}",
    )


def calculate_and_plot_intra_volatility(
    data, stock, api_one_year_ago_str, api_today_str, output_base_dir, date_folder_name
):
    output_directory = os.path.join(output_base_dir, date_folder_name, "intra_vix")
    os.makedirs(output_directory, exist_ok=True)

    print(f"\nProcessing intra-day volatility for stock: {stock}")

    # Calculate intra-day volatility (iv)
    required_cols = [
        "CH_TRADE_HIGH_PRICE",
        "CH_TRADE_LOW_PRICE",
        "CH_PREVIOUS_CLS_PRICE",
    ]
    if not all(col in data.columns for col in required_cols):
        print(f"Missing required columns for {stock}. Skipping intra-day volatility.")
        return

    data["iv"] = (
        (data["CH_TRADE_HIGH_PRICE"] - data["CH_TRADE_LOW_PRICE"])
        / data["CH_PREVIOUS_CLS_PRICE"]
    ) * 100
    data.dropna(subset=["iv"], inplace=True)
    if data["iv"].empty:
        print(f"No 'iv' values to plot for {stock} after calculation. Skipping.")
        return

    safe_stock_name = "".join(c if c.isalnum() else "_" for c in stock)
    image_filename = f"{safe_stock_name}_intra_vix.png"
    output_filepath = os.path.join(output_directory, image_filename)
    plot_volatility_histogram(
        data,
        "iv",
        stock,
        output_filepath,
        f"Intra-day Volatility (iv) Histogram for {stock}\nData: {api_one_year_ago_str} to {api_today_str}",
    )


def main():
    try:
        fno_stocks = fnolist()
        if not fno_stocks:
            print("No F&O stocks found. Exiting.")
            return
    except Exception as e:
        print(f"Error fetching F&O stock list: {e}")
        return

    today_dt = datetime.now()
    one_year_ago_dt = today_dt - timedelta(days=365)
    output_base_dir = "output"
    api_today_str = today_dt.strftime("%d-%m-%Y")
    date_folder_name = today_dt.strftime("%Y-%m-%d")
    api_one_year_ago_str = one_year_ago_dt.strftime("%d-%m-%Y")

    # Ensure base and date folders exist
    os.makedirs(os.path.join(output_base_dir, date_folder_name), exist_ok=True)

    # Process each stock
    for stock in fno_stocks:
        # Fetch data once for each stock
        data = fetch_and_clean_data(stock, api_one_year_ago_str, api_today_str)
        if data is None:
            continue

        # Calculate and plot both metrics using the same data
        calculate_and_plot_daily_volatility(
            data,
            stock,
            api_one_year_ago_str,
            api_today_str,
            output_base_dir,
            date_folder_name,
        )
        calculate_and_plot_intra_volatility(
            data,
            stock,
            api_one_year_ago_str,
            api_today_str,
            output_base_dir,
            date_folder_name,
        )

    print("\nProcessing complete.")


if __name__ == "__main__":
    main()
