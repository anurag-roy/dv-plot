# dv-plot

![ADANIGREEN](https://github.com/user-attachments/assets/52d9ff33-185e-414a-ba71-b3d13b202ebb)

A Python tool to fetch, analyze, and visualize daily volatility (dv) for all F&O stocks from the NSE India website. For each stock, it calculates daily volatility over the past year and generates a histogram plot, saving the results in a date-specific output folder.

## Features

- Fetches F&O stock list and historical price data from NSE India
- Calculates daily volatility: `(CH_CLOSING_PRICE - CH_PREVIOUS_CLS_PRICE) / CH_PREVIOUS_CLS_PRICE`
- Plots histograms of daily volatility for each stock
- Saves plots (PNG) in a nested output folder by date
- Optionally (commented in code): saves cleaned data with dv to CSV

## Requirements

- Python >= 3.13
- [matplotlib](https://matplotlib.org/) >= 3.10.3
- [nsepython](https://github.com/1analyst/nsepython) >= 2.94
- [pandas](https://pandas.pydata.org/) >= 2.2.3

## Usage

Run the main script:

```bash
uv run main.py
```

- The script will fetch the F&O stock list, download one year of daily price data for each, calculate daily volatility, and plot a histogram for each stock.
- Plots are saved as PNG files in a folder like `output/YYYY-MM-DD/` (date is set in the script).

## Output

- Each stock's histogram is saved as `<STOCKNAME>.png` in the output folder for the run date (e.g., `output/2025-05-17/`).
- The output folder is created automatically if it does not exist.
- (Optional) You can uncomment code in `main.py` to also save the cleaned data with dv as CSV files.

## License

MIT License (add your license here if different)
