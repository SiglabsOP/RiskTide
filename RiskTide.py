import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import pickle  # For saving the portfolio data
import webbrowser  # For clickable links
import subprocess

def run_external_scripts():
    # Run RiskTide Horizon.py and wait for it to finish
    subprocess.run(["python", "RiskTide Horizon.py"])
    
    # After Horizon finishes, run RiskTide Metrics.py
    subprocess.run(["python", "RiskTide Metrics.py"])
    
    
class GradientButton(tk.Canvas):
    def __init__(self, parent, text, command=None, colors=("blue", "lightblue"), font=("Arial", 12, "bold"), **kwargs):
        super().__init__(parent, **kwargs)
        self.command = command
        self.colors = colors
        self.text = text
        self.font = font

        self.create_rectangle(0, 0, self.winfo_reqwidth(), self.winfo_reqheight(), fill="", outline="")
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        self._draw_gradient()

    def _draw_gradient(self):
        """Draw gradient on the button."""
        width = self.winfo_width() if self.winfo_width() > 0 else 100
        height = self.winfo_height() if self.winfo_height() > 0 else 30
        gradient_steps = 100
        r1, g1, b1 = self.winfo_rgb(self.colors[0])
        r2, g2, b2 = self.winfo_rgb(self.colors[1])
        r_ratio = (r2 - r1) / gradient_steps
        g_ratio = (g2 - g1) / gradient_steps
        b_ratio = (b2 - b1) / gradient_steps

        for i in range(gradient_steps):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = f"#{nr >> 8:02x}{ng >> 8:02x}{nb >> 8:02x}"
            self.create_rectangle(0, i * height // gradient_steps, width, (i + 1) * height // gradient_steps, outline=color, fill=color)

        self.create_text(width // 2, height // 2, text=self.text, font=self.font, fill="white", tags="text")

    def on_click(self, event=None):
        if self.command:
            self.command()

    def on_hover(self, event=None):
        """Change color slightly on hover."""
        self.colors = ("#5A9", "#3A7")  # Adjusted hover colors
        self._draw_gradient()

    def on_leave(self, event=None):
        """Revert to original color on leave."""
        self.colors = ("blue", "lightblue")
        self._draw_gradient()


    
    
# Portfolio Management GUI
class RiskTideGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RiskTide - Portfolio Risk Manager")
        self.root.geometry("1200x800")
        self.root.state('zoomed')  # Maximizes on start
        self.root.config(bg="#2D3E50")  # Dark blue-gray background
        self.root.resizable(True, True)
        
        # Buttons for Calculations and Display
        self.calculate_button = tk.Button(self.root, text="Calculate Risk Metrics", font=("Arial", 12, "bold"), fg="white", bg="#4A90E2", command=self.calculate_risk_metrics)
        self.calculate_button.pack(pady=10)

        style = ttk.Style()
        
        # Configure Treeview background, foreground, row height, and field background
        style.configure("Treeview",
                        background="#E8F1FB",  # Lighter background color for the rows
                        foreground="black",
                        rowheight=30,  # Increased row height for better visual appeal
                        fieldbackground="#F2F9FF",  # Subtle light blue for better contrast
                        borderwidth=1,  # Adds border to each row
                        relief="flat",  # Flat relief for rows, more modern look
                        highlightthickness=1,  # Adds slight highlight border
                        highlightcolor="#4A90E2")  # Highlight color for focus
        
        # Add a hover effect for rows (change color when hovered over)
        style.map("Treeview", 
                  background=[("active", "#D1E8FF"),  # Light blue when hovered
                              ("selected", "#4A90E2")])  # Bright blue when selected
                  
        # Adding alternating row colors for better readability
        style.configure("Treeview",
                        rowalternatingbackground="#F9F9F9")  # Alternating light gray rows
        
        # Configure heading style with bold font, gradient background, shadow, and contrasting text
        style.configure("Treeview.Heading",
                        font=("Helvetica", 14, "bold"),
                        background="#4A90E2",  # Bright blue background for headings
                        foreground="black",  # Black text color for better readability
                        borderwidth=2,  # Adds border around headings
                        relief="ridge",  # Ridge effect for headings
                        anchor="center",  # Center-align column headings
                        padx=10,  # Adds some padding on the left and right of the header text
                        pady=5)  # Adds padding on the top and bottom of the header text
        
        # Adding a subtle shadow effect to the headings for a more sophisticated look
        style.map("Treeview.Heading",
                  background=[("active", "#005BA1")])  # Slightly darker shade when active
            



        # Title Label
        self.title_label = tk.Label(self.root, text="RiskTide v81.180 - Portfolio Management", font=("Arial", 24, "bold"), fg="white", bg="#2D3E50")
        self.title_label.pack(pady=20)

        # Portfolio Management Section
        self.portfolio_frame = tk.Frame(self.root, bg="#2D3E50")
        self.portfolio_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.treeview_frame = tk.Frame(self.portfolio_frame, bg="#2D3E50")
        self.treeview_frame.pack(fill="both", expand=True)

        # Scrollbars for Treeview
        self.scrollbar_x = tk.Scrollbar(self.treeview_frame, orient="horizontal")
        self.scrollbar_x.pack(side="bottom", fill="x")

        self.scrollbar_y = tk.Scrollbar(self.treeview_frame, orient="vertical")
        self.scrollbar_y.pack(side="right", fill="y")
        self.columns = ("Stock Ticker", "Date Purchased", "Units Purchased", "Purchase Price", "Total Purchase Price")

        # Place the Treeview inside the treeview_frame instead of root
        self.tree = ttk.Treeview(self.treeview_frame, columns=self.columns, show="headings", height=10)
        
        # Configure columns and headings
        for col in self.columns:
            self.tree.heading(col, text=col, anchor="center", command=lambda c=col: self.sort_column(c, False))
            self.tree.column(col, anchor="center", width=150)
        
        # Pack the Treeview and scrollbars within the frame
        self.tree.pack(fill="both", expand=True)
        self.scrollbar_y.config(command=self.tree.yview)
        self.scrollbar_x.config(command=self.tree.xview)
        self.tree.config(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

        # Add Stock Button
        # Buttons with Gradient
        # Add Stock Button
        self.add_button = tk.Button(self.portfolio_frame, text="Add Stock", font=("Arial", 12, "bold"), fg="white", bg="#4A90E2", command=self.add_stock_modal)
        self.add_button.pack(pady=10)
        
        # Delete Entry Button
        self.delete_button = tk.Button(self.portfolio_frame, text="Delete Entry", font=("Arial", 12, "bold"), fg="white", bg="#E94E77", command=self.delete_entry)
        self.delete_button.pack(pady=10)
        
        # About and Help Buttons
        self.about_button = tk.Button(self.root, text="About", font=("Arial", 12, "bold"), fg="white", bg="#4A90E2", command=self.show_about_modal)
        self.about_button.pack(pady=10)
        
        self.help_button = tk.Button(self.root, text="Help", font=("Arial", 12, "bold"), fg="white", bg="#4A90E2", command=self.show_help_modal)
        self.help_button.pack(pady=10)
        
        # Result Label
        self.result_label = tk.Label(self.root, text="(c) 2024 SIG Labs", font=("Arial", 14), fg="white", bg="#2D3E50", justify="left")
        self.result_label.pack(pady=10)

        # Load portfolio from file
        self.load_portfolio()

    def delete_entry(self):
        """Delete the selected entry from the portfolio."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No entry selected to delete.")
            return

        for item in selected_item:
            self.tree.delete(item)

        self.save_portfolio()
        messagebox.showinfo("Success", "Entry deleted successfully!")

    def save_portfolio(self):
        """Save the portfolio to a file using pickle"""
        portfolio_data = []
        for row in self.tree.get_children():
            stock_data = self.tree.item(row)["values"]
            portfolio_data.append(stock_data)
        
        with open("portfolio.pkl", "wb") as f:
            pickle.dump(portfolio_data, f)
    
        # Save as CSV file
        portfolio_df = pd.DataFrame(portfolio_data, columns=self.columns)  # Use all columns
        portfolio_df.to_csv('portfolio_data.csv', index=False)

    def load_portfolio(self):
        """Load the portfolio from a file"""                                         
        try:
            with open("portfolio.pkl", "rb") as f:
                portfolio_data = pickle.load(f)
                for stock_data in portfolio_data:
                    self.tree.insert("", "end", values=stock_data)
        except FileNotFoundError:
            pass  # No portfolio file found, nothing to load

    def sort_column(self, col, reverse):
        data = [(self.tree.set(item, col), item) for item in self.tree.get_children("")]
        
        # Custom sorting for different column types
        if col in ["Units Purchased", "Purchase Price", "Total Purchase Price"]:
            # Sort numerically
            data.sort(key=lambda x: float(x[0]), reverse=reverse)
        elif col == "Date Purchased":
            # Sort dates
            data.sort(key=lambda x: pd.to_datetime(x[0], format="%d-%m-%Y"), reverse=reverse)
        else:
            # Sort alphabetically
            data.sort(key=lambda x: x[0].lower(), reverse=reverse)
        
        for index, (val, item) in enumerate(data):
            self.tree.move(item, "", index)
        
        # Reverse sort next time
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def add_stock_modal(self):
        """Open a modal dialog for adding a stock."""
        modal = tk.Toplevel(self.root)
        modal.title("Add Stock")
        modal.geometry("800x600")
        modal.grab_set()  # Make it modal
        modal.state('zoomed')  # Maximizes on open

        tk.Label(modal, text="Stock Ticker:", font=("Arial", 12)).pack(pady=10)
        stock_ticker_entry = tk.Entry(modal, font=("Arial", 12))
        stock_ticker_entry.pack(pady=5)

        tk.Label(modal, text="Date Purchased (DD-MM-YYYY):", font=("Arial", 12)).pack(pady=10)
        date_purchased_entry = tk.Entry(modal, font=("Arial", 12))
        date_purchased_entry.pack(pady=5)

        tk.Label(modal, text="Units Purchased:", font=("Arial", 12)).pack(pady=10)
        units_purchased_entry = tk.Entry(modal, font=("Arial", 12))
        units_purchased_entry.pack(pady=5)

        tk.Label(modal, text="Purchase Price:", font=("Arial", 12)).pack(pady=10)
        purchase_price_entry = tk.Entry(modal, font=("Arial", 12))
        purchase_price_entry.pack(pady=5)

        def submit_stock():
            """Handle stock submission."""
            stock_ticker = stock_ticker_entry.get()
            date_purchased = date_purchased_entry.get()
            units_purchased = units_purchased_entry.get()
            purchase_price = purchase_price_entry.get()

            if not stock_ticker or not date_purchased or not units_purchased or not purchase_price:
                messagebox.showerror("Input Error", "Please fill in all fields.")
                return

            try:
                total_purchase_price = float(units_purchased) * float(purchase_price)
                stock_data = (stock_ticker, date_purchased, units_purchased, purchase_price, total_purchase_price)
                self.tree.insert("", "end", values=stock_data)
                self.save_portfolio()
                modal.destroy()  # Close the modal dialog
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add stock: {e}")

        tk.Button(modal, text="Submit", font=("Arial", 12, "bold"), command=submit_stock).pack(pady=20)

    def calculate_risk_metrics(self):
        """Load and display risk metrics from CSV in a tidy modal."""
        try:
            # Load the stock metrics summary from the CSV file
            stock_metrics_df = pd.read_csv('stock_metrics_summary.csv')
    
            # Create a new modal window to display the data
            metrics_modal = tk.Toplevel(self.root)
            metrics_modal.title("Risk Metrics Summary")
            metrics_modal.geometry("900x700")
            metrics_modal.grab_set()  # Make it modal
            metrics_modal.state('zoomed')  # Maximizes on open
    
            # Create a frame for the title
            title_frame = tk.Frame(metrics_modal, bg="#2D3E50")
            title_frame.pack(fill="x", pady=10)
            
            # Title label
            title_label = tk.Label(title_frame, text="Risk Metrics Summary", font=("Arial", 18, "bold"), fg="white", bg="#2D3E50")
            title_label.pack(padx=20, pady=10)
    
            # Create a frame for the data
            data_frame = tk.Frame(metrics_modal, bg="#2D3E50")
            data_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
            # Create a treeview to display the data with customized columns
            columns = stock_metrics_df.columns.tolist()
            tree = ttk.Treeview(data_frame, columns=columns, show="headings", height=12)
    
            # Set column headings and style
            for col in columns:
                tree.heading(col, text=col, anchor="center")
                tree.column(col, anchor="center", width=150)  # Set the column width
    
            # Insert the data into the treeview
            for _, row in stock_metrics_df.iterrows():
                tree.insert("", "end", values=row.tolist())
    
            # Add scrollbars for the treeview
            scrollbar_y = tk.Scrollbar(data_frame, orient="vertical", command=tree.yview)
            scrollbar_y.pack(side="right", fill="y")
            tree.config(yscrollcommand=scrollbar_y.set)
    
            scrollbar_x = tk.Scrollbar(data_frame, orient="horizontal", command=tree.xview)
            scrollbar_x.pack(side="bottom", fill="x")
            tree.config(xscrollcommand=scrollbar_x.set)
    
            tree.pack(fill="both", expand=True)
    
            # Add a close button at the bottom
            close_frame = tk.Frame(metrics_modal, bg="#2D3E50")
            close_frame.pack(fill="x", pady=10)
    
            close_button = tk.Button(close_frame, text="Close", font=("Arial", 12, "bold"), command=metrics_modal.destroy, fg="white", bg="#E94E77")
            close_button.pack(pady=10)
    
        except FileNotFoundError:
            messagebox.showerror("INFO", "Please add data to the portfolio in order for the software to work.")
        except pd.errors.EmptyDataError:
        # Custom dialog for empty file
            messagebox.showinfo("INFO", "Please add more data first to your portfolio. Between 30 and 100 entries are recommended for metrics to function properly.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load risk metrics: {e}")

    def show_about_modal(self):
        """Display the About modal with information about the app."""
        about_modal = tk.Toplevel(self.root)
        about_modal.title("About")
        about_modal.geometry("600x400")
        about_modal.grab_set()  # Make it modal
        about_modal.state('zoomed')  # Maximizes on open
        about_modal.iconbitmap('logo.ico')


        about_label = tk.Label(about_modal, text="RiskTide Portfolio Management v81.180\n\nDeveloped by Peter De Ceuster", font=("Arial", 16), fg="black")
        about_label.pack(pady=20)

        link_label = tk.Label(about_modal, text="Buy me a coffee", fg="blue", cursor="hand2")
        link_label.pack(pady=10)
        link_label.bind("<Button-1>", lambda e: webbrowser.open("https://buymeacoffee.com/siglabo"))
        
        link_label = tk.Label(about_modal, text="Visit my website", fg="blue", cursor="hand2")
        link_label.pack(pady=10)
        link_label.bind("<Button-1>", lambda e: webbrowser.open("https://peterdeceuster.uk/index2.html"))

    def show_help_modal(self):
            """Display the Help modal with detailed guidance."""
            help_modal = tk.Toplevel(self.root)
            help_modal.title("Help")
            help_modal.geometry("800x600")
            help_modal.grab_set()  # Make it modal
            help_modal.state('zoomed')  # Maximizes on open
 
            # Frame to hold the scrollable text area
            frame = tk.Frame(help_modal)
            frame.pack(fill=tk.BOTH, expand=True)
            help_modal.iconbitmap('logo.ico')

            # Canvas widget for scrolling
            canvas = tk.Canvas(frame)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
            # Scrollbars (both vertical and horizontal)
            scrollbar_y = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
            scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
            scrollbar_x = tk.Scrollbar(help_modal, orient=tk.HORIZONTAL, command=canvas.xview)
            scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
    
            # Configure canvas scrolling
            canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
    
            # Create another frame inside the canvas
            help_content_frame = tk.Frame(canvas)
            canvas.create_window((0, 0), window=help_content_frame, anchor="nw")

            help_text = """This is your portfolio risk management software. You can:
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
        
        # Create the Text widget inside the frame
            help_label = tk.Label(help_content_frame, text=help_text, font=("Arial", 12), justify="left")
            help_label.pack(padx=20, pady=20)

        # Update scrollregion to the size of the content
            help_content_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))

        # Event bindings to update scrollbar if content changes
            help_modal.bind("<Configure>", lambda event, canvas=canvas: canvas.config(scrollregion=canvas.bbox("all")))

        # Add close button
            close_button = tk.Button(help_modal, text="Close", command=help_modal.destroy)
            close_button.pack(pady=10)

# Create the main application window
root = tk.Tk()

# Instantiate the RiskTideGUI class
app = RiskTideGUI(root)

# Start the Tkinter event loop
run_external_scripts()

root.mainloop()
