import pandas as pd
import numpy as np
from scipy.stats import kurtosis, skew
from sklearn.linear_model import LinearRegression
import os
import time
from datetime import datetime, timedelta

import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
def silent_excepthook(exc_type, exc_value, traceback):
    pass  # Do nothing; suppress output

sys.excepthook = silent_excepthook
# Load SPY data (benchmark)
spy_data = pd.read_csv('spy_data.csv')
spy_data['Date'] = pd.to_datetime(spy_data['Date'])
spy_data['SPY Return'] = spy_data['Close'].pct_change()

# Load portfolio data
portfolio_data = pd.read_csv('portfolio_data.csv')  # File containing tickers and other info

# Specify the correct date format for 'Date Purchased'
portfolio_data['Date Purchased'] = pd.to_datetime(portfolio_data['Date Purchased'], format='%d-%m-%Y', errors='coerce')

# Drop rows with invalid 'Date Purchased'
portfolio_data = portfolio_data.dropna(subset=['Date Purchased'])

# Summary metrics list
summary_metrics = []



def clean_all_temp_files(temp_file_pattern="*_data_*.csv"):
    """
    Removes all files matching the specified pattern.

    :param temp_file_pattern: The pattern used to identify files for deletion.
    """
    temp_files_removed = 0

    for file_name in os.listdir('.'):
        # Check if the file matches the pattern
        if "_data_" in file_name and file_name.endswith('.csv'):
            try:
                # Delete the file
                os.remove(file_name)
                temp_files_removed += 1
                print(f"Deleted temporary file: {file_name}")
            except Exception as e:
                print(f"Error deleting file {file_name}: {e}")

    if temp_files_removed == 0:
        print("No temporary files found.")
    else:
        print(f"Total temporary files removed: {temp_files_removed}")

# Call the function before starting the main workflow
clean_all_temp_files()

        
# Function to process each stock independently
def process_stock(stock):
    stock_metrics = {}
    try:
        # Check if data file exists
        stock_file = f'{stock.lower()}_data.csv'
        if not os.path.exists(stock_file):
            print(f"Data file for stock {stock} not found. Creating temporary file.")
            
            # Filter matching rows from the original portfolio data
            stock_rows = portfolio_data[portfolio_data['Stock Ticker'] == stock]
            
            # If there are any rows for the stock, create a temporary file with all the entries
            if not stock_rows.empty:
                temp_file = f"{stock.lower()}_data_{pd.to_datetime('now').strftime('%Y%m%d%H%M%S')}.csv"
                stock_rows.to_csv(temp_file, index=False)
                print(f"Temporary data file created for {stock} at {temp_file}")
                
                # Proceed to process stock data
                stock_data = stock_rows.copy()
                stock_data['Date'] = pd.to_datetime(stock_data['Date Purchased'])
                stock_data['Stock Return'] = stock_data['Purchase Price'].pct_change()
                
                # Merge with SPY benchmark data
                merged_data = pd.merge(
                    stock_data[['Date', 'Stock Return']],
                    spy_data[['Date', 'SPY Return']],
                    on='Date',
                    how='inner'
                )
                
                # Check for sufficient data after merging
                if merged_data.empty or len(merged_data) < 2:
                    print(f"Insufficient data for stock: {stock}. Skipping.")
                    return None

                # Drop rows with missing return data
                merged_data = merged_data.dropna(subset=['Stock Return', 'SPY Return'])

                # Calculate metrics
                daily_stock_return = merged_data['Stock Return']
                daily_spy_return = merged_data['SPY Return']

                # Linear regression for Alpha & Beta
                X = daily_spy_return.values.reshape(-1, 1)
                y = daily_stock_return.values
                reg = LinearRegression().fit(X, y)
                beta = reg.coef_[0]
                alpha = reg.intercept_
                r_squared = reg.score(X, y)

                # Sharpe Ratio
                sharpe_ratio = daily_stock_return.mean() / daily_stock_return.std()

                # Sortino Ratio
                downside_std = daily_stock_return[daily_stock_return < 0].std()
                sortino_ratio = daily_stock_return.mean() / downside_std if downside_std > 0 else np.nan

                # Treynor Ratio
                treynor_ratio = daily_stock_return.mean() / beta if beta != 0 else np.nan

                # Omega Ratio
                threshold = 0
                positive_returns = daily_stock_return[daily_stock_return > threshold].sum()
                negative_returns = -daily_stock_return[daily_stock_return < threshold].sum()
                omega_ratio = positive_returns / negative_returns if negative_returns > 0 else np.nan

                # Kurtosis and Skewness
                kurt = kurtosis(daily_stock_return, fisher=True)
                skewness = skew(daily_stock_return)

                # Max Drawdown
                cumulative_return = (1 + daily_stock_return).cumprod()
                peak = cumulative_return.cummax()
                drawdown = (cumulative_return - peak) / peak
                max_drawdown = drawdown.min()

                # Value at Risk (VaR) at 95%
                var_95 = np.percentile(daily_stock_return, 5)

                # Return metrics for the stock
                stock_metrics = {
                    'Stock Ticker': stock,
                    'Alpha': alpha,
                    'Beta': beta,
                    'R²': r_squared,
                    'Sharpe Ratio': sharpe_ratio,
                    'Sortino Ratio': sortino_ratio,
                    'Treynor Ratio': treynor_ratio,
                    'Omega Ratio': omega_ratio,
                    'Kurtosis': kurt,
                    'Skewness': skewness,
                    'Max Drawdown': max_drawdown,
                    'VaR (95%)': var_95
                }

                # Delete the temporary file after processing
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    print(f"Temporary file for {stock} deleted successfully.")
                
    except Exception as e:
        print(f"Error processing stock {stock}: {e}. Skipping.")
        return None

    return stock_metrics

# Use ThreadPoolExecutor to parallelize the processing of each stock
with ThreadPoolExecutor() as executor:
    futures = [executor.submit(process_stock, stock) for stock in portfolio_data['Stock Ticker'].unique()]
    
    for future in as_completed(futures):
        result = future.result()
        if result:
            summary_metrics.append(result)

# Convert metrics list to DataFrame
summary_df = pd.DataFrame(summary_metrics)

# Display results
print("\nSummary Metrics for All Stocks:")
print(summary_df)

# Optional: Save results to a CSV file
summary_df.to_csv('stock_metrics_summary.csv', index=False)
