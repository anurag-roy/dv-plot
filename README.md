# dv-plot

![ADANIGREEN](https://github.com/user-attachments/assets/52d9ff33-185e-414a-ba71-b3d13b202ebb)

A Python tool to fetch, analyze, and visualize both daily volatility (dv) and intra-day volatility (iv) for all F&O stocks from the NSE India website. For each stock, it calculates volatilities over the past year and generates histogram plots, saving the results in a date-specific output folder.

## Features

- Fetches F&O stock list and historical price data from NSE India
- Calculates daily volatility: `(CH_CLOSING_PRICE - CH_PREVIOUS_CLS_PRICE) / CH_PREVIOUS_CLS_PRICE * 100`
- Calculates intra-day volatility: `(CH_TRADE_HIGH_PRICE - CH_TRADE_LOW_PRICE) / CH_PREVIOUS_CLS_PRICE * 100`
- Plots histograms of both volatility metrics for each stock
  - Bins are centered on mean with width equal to standard deviation
  - X-axis labels show standard deviation intervals
- Saves plots (PNG) in nested output folders by date and metric type

## Requirements

- Python >= 3.13
- [matplotlib](https://matplotlib.org/) >= 3.10.3
- [nsepython2](https://pypi.org/project/nsepython2/) >= 0.1.0
- [pandas](https://pandas.pydata.org/) >= 2.2.3
- [urllib3](https://urllib3.readthedocs.io/) >= 2.4.0

## Usage

Run the main script:

```bash
uv run main.py
```

- The script will fetch the F&O stock list, download one year of daily price data for each stock
- For each stock, it calculates both daily and intra-day volatility and plots histograms
- Plots are saved as PNG files in date-specific folders with metric-specific subfolders
- The date folder uses the current date in DD-MM-YYYY format

## Output Structure

```
output/
└── YYYY-MM-DD/
    ├── daily_vix/
    │   └── <STOCKNAME>_daily_vix.png
    └── intra_vix/
        └── <STOCKNAME>_intra_vix.png
```

- Output folders are created automatically if they do not exist
- Each stock gets two plots: one for daily volatility and one for intra-day volatility
- Plots include statistical information (mean, standard deviation, median)

## License

[MIT License](LICENSE)
