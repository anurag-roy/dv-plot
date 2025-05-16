import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os # Added for directory creation
from nsepython import fnolist, equity_history

def calculate_and_plot_volatility():
    """
    Fetches stock data, calculates daily volatility,
    and plots a histogram for each stock, saving it to a nested date-specific folder.
    """
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

    # Define base output directory and the specific date folder
    output_base_dir = "output"
    date_folder_name = "2025-05-17" # Using the specified date for the folder
    
    # Construct the full path for the day's output
    output_directory_for_today = os.path.join(output_base_dir, date_folder_name)

    # API date formats
    api_today_str = today_dt.strftime("%d-%m-%Y")
    api_one_year_ago_str = one_year_ago_dt.strftime("%d-%m-%Y")

    # Create the nested directory (e.g., output/2025-05-17) if it doesn't exist
    # os.makedirs will create parent directories as needed (like 'output')
    try:
        os.makedirs(output_directory_for_today, exist_ok=True) # exist_ok=True prevents error if dir already exists
        print(f"Ensured directory '{output_directory_for_today}' exists.")
    except OSError as e:
        print(f"Error creating directory '{output_directory_for_today}': {e}")
        return # Exit if directory creation fails

    for stock in fno_stocks:
        print(f"\nProcessing stock: {stock}")
        try:
            # Fetch equity history for the stock
            data = equity_history(stock, "EQ", api_one_year_ago_str, api_today_str)

            if data is None or data.empty:
                print(f"No data returned for {stock}. Skipping.")
                continue

            # Ensure required columns are present
            required_cols = ['CH_CLOSING_PRICE', 'CH_PREVIOUS_CLS_PRICE']
            if not all(col in data.columns for col in required_cols):
                print(f"Missing required columns for {stock}. Available: {data.columns}. Skipping.")
                continue

            # Convert price columns to numeric, coercing errors to NaN
            data['CH_CLOSING_PRICE'] = pd.to_numeric(data['CH_CLOSING_PRICE'], errors='coerce')
            data['CH_PREVIOUS_CLS_PRICE'] = pd.to_numeric(data['CH_PREVIOUS_CLS_PRICE'], errors='coerce')

            # Drop rows where conversion might have failed or prices are zero/negative
            data.dropna(subset=['CH_CLOSING_PRICE', 'CH_PREVIOUS_CLS_PRICE'], inplace=True)
            # Avoid division by zero or issues with non-positive previous close prices
            data = data[data['CH_PREVIOUS_CLS_PRICE'] > 0] 

            if data.empty:
                print(f"Not enough valid data to calculate volatility for {stock} after cleaning. Skipping.")
                continue

            # Calculate daily volatility (dv)
            # dv = (CH_CLOSING_PRICE - CH_PREVIOUS_CLS_PRICE) / CH_PREVIOUS_CLS_PRICE
            data['dv'] = (data['CH_CLOSING_PRICE'] - data['CH_PREVIOUS_CLS_PRICE']) / data['CH_PREVIOUS_CLS_PRICE']

            # Drop NaN values in 'dv' column that might result from the calculation
            data.dropna(subset=['dv'], inplace=True)

            if data['dv'].empty:
                print(f"No 'dv' values to plot for {stock} after calculation. Skipping.")
                continue

            # Plot histogram for 'dv'
            plt.figure(figsize=(12, 7))
            n_bins = min(50, max(10, int(len(data['dv'])**0.5))) 
            plt.hist(data['dv'], bins=n_bins, edgecolor='black', alpha=0.75, color='deepskyblue') # Changed color slightly
            
            plt.title(f'Daily Volatility (dv) Histogram for {stock}\nData: {api_one_year_ago_str} to {api_today_str}', fontsize=15, fontweight='bold')
            plt.xlabel('Daily Volatility (dv)', fontsize=13)
            plt.ylabel('Frequency', fontsize=13)
            plt.grid(axis='y', linestyle=':', alpha=0.6) # Changed grid style
            plt.xticks(fontsize=11)
            plt.yticks(fontsize=11)
            
            # Add a text box with some stats if dv is not empty
            if not data['dv'].empty:
                mean_dv = data['dv'].mean()
                std_dv = data['dv'].std()
                median_dv = data['dv'].median()
                stats_text = f'Mean: {mean_dv:.4f}\nStd Dev: {std_dv:.4f}\nMedian: {median_dv:.4f}'
                plt.text(0.05, 0.95, stats_text, transform=plt.gca().transAxes, fontsize=10,
                         verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.5))

            plt.tight_layout()


            # Save the histogram as a PNG file inside the nested date-specific folder
            safe_stock_name = "".join(c if c.isalnum() else "_" for c in stock)
            # The filename itself does not need the folder structure, os.path.join handles it
            image_filename = f"{safe_stock_name}.png"
            output_filepath = os.path.join(output_directory_for_today, image_filename)
            
            try:
                plt.savefig(output_filepath)
                print(f"Histogram saved as {output_filepath}")
            except Exception as e:
                print(f"Error saving histogram for {stock} to {output_filepath}: {e}")
            plt.close() # Close the plot to free up memory

            # Optionally, save the data with 'dv' to a CSV inside the date-specific folder
            # csv_filename_with_dv = f"{safe_stock_name}_with_dv.csv"
            # output_csv_filepath = os.path.join(output_directory_for_today, csv_filename_with_dv)
            # try:
            #     data.to_csv(output_csv_filepath, index=False)
            #     print(f"Data with dv saved to {output_csv_filepath}")
            # except Exception as e:
            #     print(f"Error saving CSV with dv for {stock} to {output_csv_filepath}: {e}")

        except Exception as e:
            print(f"An error occurred while processing {stock}: {e}")
            # For detailed debugging:
            # import traceback
            # print(traceback.format_exc())

if __name__ == "__main__":
    calculate_and_plot_volatility()
    print("\nProcessing complete.")
