# RiskTide 
RiskTide 81.180 
 
 # RiskTide Portfolio Risk Manager v81.180

RiskTide is a comprehensive portfolio risk management software designed to help investors track, analyze, and optimize their stock portfolios. This powerful tool combines an intuitive graphical interface with advanced risk metrics calculations to provide valuable insights into your investment strategy.

## Features

### Portfolio Management
- Add stocks to your portfolio with details like ticker, purchase date, units, and price.
- View your portfolio in a sortable, customizable treeview.
- Delete entries from your portfolio.
- Automatically save and load portfolio data.

### Risk Metrics Calculation
- Calculate and display a wide range of risk metrics for your portfolio.
- Metrics include:
  - Alpha
  - Beta
  - R²
  - Sharpe Ratio
  - Sortino Ratio
  - Treynor Ratio
  - Omega Ratio
  - Kurtosis
  - Skewness
  - Max Drawdown
  - Value at Risk (VaR)
- Utilizes S&P 500 (SPY) data as a benchmark, fetched from Kaggle.

### User Interface
- Clean, modern interface with a dark blue-gray theme.
- Responsive design with resizable windows.
- Gradient buttons for improved visual appeal.
- Sortable treeview columns for easy data organization.

### Additional Features
- About section with developer information and donation links.
- Comprehensive help modal with detailed guidance on using the software.

## Installation

 

  Ensure you have a Kaggle API key set up in your user directory under `.kaggle/kaggle.json`.

## Usage

1. Run the main script:
 

2. Use the interface to add stocks, manage your portfolio, and calculate risk metrics.
3. For optimal results, aim to have between 30 and 100 trade entries in your portfolio.

## Risk Metrics Calculation

RiskTide calculates the following risk metrics for your portfolio:
- **Alpha**: Measures excess return compared to a benchmark.
- **Beta**: Measures volatility relative to the market.
- **R²**: Shows how well the asset follows the market.
- **Sharpe Ratio**: Measures return per unit of risk.
- **Sortino Ratio**: Focuses on downside risk.
- **Treynor Ratio**: Measures returns per unit of market risk.
- **Omega Ratio**: Compares the likelihood of achieving returns to falling short.
- **Kurtosis**: Measures the probability of extreme events.
- **Skewness**: Measures asymmetry of returns.
- **Max Drawdown**: The maximum observed loss from a peak to a trough.
- **Value at Risk (VaR)**: The potential loss in value of a portfolio over a defined period.

## Data Management

### SPY Data Fetching (RiskTide Horizon)
RiskTide automatically fetches S&P 500 (SPY) data from Kaggle using the following process:
- Checks if the `spy_data.csv` file exists locally.
- If the file doesn't exist or is older than a month, it downloads fresh data.
- Uses Kaggle API to fetch the latest SPY dataset.
- Renames and moves the downloaded file to the appropriate location.
- Records the last download time to manage update frequency.

### Stock Data Processing (RiskTide Metrics)
The program processes and stores stock data as follows:
- Loads portfolio data from `portfolio_data.csv`.
- For each stock in the portfolio:
  - Creates temporary data files if necessary.
  - Calculates risk metrics using historical price data.
  - Merges stock data with SPY benchmark data.
  - Computes various risk metrics using statistical and financial formulas.
  - Summarizes metrics for all stocks in the portfolio.
- Saves the summary to `stock_metrics_summary.csv`.

## Dependencies
- `tkinter`
- `pandas`
- `numpy`
- `scipy`
- `sklearn`
- `kaggle`
- `webbrowser`
- `subprocess`

## Data Source
- S&P 500 historical data is fetched from Kaggle. https://www.kaggle.com/datasets/henryhan117/sp-500-historical-data



From the RiskTide documentation:

This is your portfolio risk management software. You can:
        1. Add stocks to your portfolio
        2. Calculate your portfolio's risk metrics
        3. Delete entries from your portfolio
        4. View risk metrics in a detailed modal
        
        Risk Metrics:
        The SPY is fetched from kaggle, so you need your kaggle APIkey (a json file) placed inside of 
        your windows user directory under a dir called /.kaggle 
        The SPY is fetched monthly, or when the datafile is not found, it is fetched too.
        For decent outcome, you need around 30 to 100 trades recorded, and beyond 100 the accuracy will improve of the metrics.
        The kaggle source is https://www.kaggle.com/datasets/henryhan117/sp-500-historical-data
        
        - **Alpha**: Measures excess return compared to a benchmark. High alpha indicates outperformance.
        - **Beta**: Measures volatility relative to the market. High beta means more risk.
        - **R²**: Shows how well the asset follows the market. Higher R² means stronger correlation.
        - **Sharpe Ratio**: Measures return per unit of risk. Higher is better for risk-adjusted returns.
        - **Sortino Ratio**: Focuses on downside risk. Higher is better for protecting against loss.
        - **Treynor Ratio**: Measures returns per unit of market risk. Higher is better for efficient returns.
        - **Omega Ratio**: Compares the likelihood of achieving returns to falling short. Higher is better.
        - **Kurtosis**: Measures the probability of extreme events. Higher indicates more risk from extremes.
        - **Skewness**: Measures asymmetry. Positive skew suggests more potential for large gains.
        - **Max Drawdown**: The largest loss from a peak. Lower is better for less risk.
        - **VaR (95%)**: The potential loss at a 95% confidence level. Lower VaR indicates lower risk.
        
        EXTENSIVE METRICS INFORMATION:  
               
        Page 1: Understanding Risk Metrics
        
        Alpha: Measures the excess return of an investment relative to the return of a benchmark index (such as the S&P 500).
        - Low: Negative or close to zero, indicating underperformance.
        - Medium: Around 0, suggesting the investment is tracking the market.
        - High: Positive, showing the investment is outperforming the market.
        - Interpretation: A high alpha indicates a manager's ability to provide value beyond the market's performance.
        
        Beta: Measures the volatility (or risk) of an asset compared to the market.
        - Low: Below 1, indicating less volatility than the market.
        - Medium: Around 1, meaning the asset moves in line with the market.
        - High: Above 1, showing higher volatility than the market.
        - Interpretation: A higher beta means higher risk but also higher potential return.
        
        R² (R-squared): Shows how well the asset's returns correlate with the market’s returns. A higher R² means the asset's movement is more predictable.
        - Low: Below 0.5, indicating weak correlation with the market.
        - Medium: 0.5-0.7, indicating some correlation.
        - High: Above 0.7, showing a strong correlation with the market.
        - Interpretation: A higher R² means the asset follows the market more closely.
        
        Page 2: Performance Metrics
        
        Sharpe Ratio: Measures the risk-adjusted return by comparing the asset's return to its volatility.
        - Low: Below 1, meaning the return isn't worth the risk.
        - Medium: 1 to 2, indicating a decent risk-return balance.
        - High: Above 2, showing high return for the risk taken.
        - Interpretation: A higher Sharpe ratio is preferable as it suggests better risk-adjusted returns.
        
        Sortino Ratio: Similar to the Sharpe Ratio but only considers downside risk (negative returns).
        - Low: Below 1, indicating poor downside protection.
        - Medium: 1 to 2, showing acceptable risk-adjusted returns.
        - High: Above 2, indicating strong risk-adjusted returns with less downside risk.
        - Interpretation: A high Sortino ratio is better, showing lower risk of loss.
        
        Treynor Ratio: Measures returns per unit of market risk (beta). It’s another risk-adjusted measure but focuses more on systemic risk.
        - Low: Below 0.1, suggesting poor performance relative to market risk.
        - Medium: 0.1 to 0.2, meaning moderate performance.
        - High: Above 0.2, indicating strong risk-adjusted returns.
        - Interpretation: Higher Treynor ratios are desirable as they indicate efficient return for market risk.
        
        Omega Ratio: Compares the probability of achieving a certain return to the probability of falling short. A higher Omega Ratio indicates better risk management.
        - Low: Below 1, suggesting more risk than reward.
        - Medium: 1 to 1.5, showing moderate returns for risk.
        - High: Above 1.5, indicating a high reward relative to risk.
        - Interpretation: A higher Omega ratio shows better overall performance.
        
        Page 3: Volatility and Risk Indicators
        
        Kurtosis: Measures the "tailedness" or extreme values of an asset's return distribution. High kurtosis indicates a higher chance of extreme events (either good or bad).
        - Low: Below 3, indicating a normal or low-risk distribution.
        - Medium: Around 3, showing a standard distribution.
        - High: Above 3, indicating more extreme fluctuations than normal.
        - Interpretation: A higher kurtosis is associated with more risk from extreme events.
        
        Skewness: Measures the asymmetry of the distribution of returns. A negative skew means more potential for large losses, while a positive skew suggests potential for large gains.
        - Low: Negative, indicating higher probability of negative returns.
        - Medium: Close to zero, meaning a fairly symmetrical return distribution.
        - High: Positive, indicating potential for large positive returns.
        - Interpretation: A positive skew is generally better as it suggests more upside potential.
        
        Max Drawdown: The maximum observed loss from a peak to a trough during a specified period.
        - Low: Below 10%, indicating minimal loss.
        - Medium: 10-30%, showing moderate loss.
        - High: Above 30%, indicating significant risk and loss.
        - Interpretation: A lower max drawdown is better as it shows less potential for large losses.
        
        VaR (Value at Risk 95%): Measures the potential loss in the value of a portfolio at a 95% confidence level.
        - Low: Small value, indicating limited potential loss.
        - Medium: Moderate value, suggesting a medium risk of loss.
        - High: High value, indicating high potential loss.
        - Interpretation: Lower VaR values are preferable as they represent less risk.
        
        Page 4: How to Use These Metrics Together
        
        Risk Management: Use a combination of metrics like Sharpe Ratio, Sortino Ratio, and Max Drawdown to assess risk-adjusted returns and extreme risks.
        Performance Evaluation: Alpha, Beta, and R² help to assess if your portfolio is performing better than the market or in line with it, and how volatile it is.
        Investment Strategy: Depending on your risk tolerance, choose metrics that align with your strategy. For example, conservative investors may focus on low Beta, low Max Drawdown, and high Sharpe Ratio, while aggressive investors may prioritize high Alpha and potential returns.
        
        By using these metrics effectively, you can better understand the performance and risks of your portfolio, and make more informed investment decisions.""" 


If you enjoy this program, buy me a coffee https://buymeacoffee.com/siglabo
You can use it free of charge or build upon my code. 
 
(c) Peter De Ceuster 2024
Software Distribution Notice: https://peterdeceuster.uk/doc/code-terms 
This software is released under the FPA General Code License.
 
 