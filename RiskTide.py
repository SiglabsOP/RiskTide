import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import pickle  # For saving the portfolio data
import webbrowser  # For clickable links
import subprocess
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
import os
from matplotlib.backends.backend_pdf import PdfPages
from tkinter import filedialog
import threading  # Add this at the top of your script
def run_external_scripts_threaded():
    """Runs external scripts in a separate thread"""
    threading.Thread(target=run_external_scripts).start()

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
        self.root.iconbitmap('logo.ico')

        # Buttons for Calculations and Display
        self.calculate_button = tk.Button(self.root, text="Calculate Risk Metrics", font=("Arial", 12, "bold"), fg="white", bg="#4A90E2", command=self.calculate_risk_metrics_threaded)



        self.calculate_button.pack(pady=10)
        
        self.graph_button = tk.Button(self.root, text="Generate Graphs", font=("Arial", 12, "bold"), fg="white", bg="#4A90E2", command=self.generate_graphs)


        self.graph_button.pack(pady=10)


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
        
        # Portfolio Management Section
        # Create a frame for the Add Stock and Delete Entry buttons
        self.portfolio_frame = tk.Frame(self.root, bg="#2D3E50")
        self.portfolio_frame.pack(fill="x", pady=10)
        
        # Add Stock Button
        self.add_button = tk.Button(self.portfolio_frame, text="Add Stock", font=("Arial", 12, "bold"), fg="white", bg="#4A90E2", command=self.add_stock_modal)
        self.add_button.pack(side=tk.LEFT, padx=10)
        
        # Delete Entry Button
        self.delete_button = tk.Button(self.portfolio_frame, text="Delete Entry", font=("Arial", 12, "bold"), fg="white", bg="#E94E77", command=self.delete_entry)
        self.delete_button.pack(side=tk.LEFT, padx=10)
        
        # Create a frame for the About, Help, and Import buttons
        self.button_frame = tk.Frame(self.root, bg="#2D3E50")
        self.button_frame.pack(fill="x", pady=10, padx=10)
        
        # About and Help Buttons
        self.about_button = tk.Button(self.button_frame, text="About", font=("Arial", 12, "bold"), fg="white", bg="#4A90E2", command=self.show_about_modal)
        self.about_button.pack(side=tk.LEFT, padx=10)
        
        self.help_button = tk.Button(self.button_frame, text="Help", font=("Arial", 12, "bold"), fg="white", bg="#4A90E2", command=self.show_help_modal)
        self.help_button.pack(side=tk.LEFT, padx=10)
        
        # Import Button
        self.import_button = tk.Button(self.button_frame, text="Jstock Import", font=("Arial", 12, "bold"), fg="white", bg="#4A90E2", command=self.import_csv_threaded)

        self.import_button.pack(side=tk.RIGHT, padx=10)  # Aligned to the right
        
        # Result Label (Positioned at the bottom of the window)
        self.result_label = tk.Label(self.root, text="(c) 2024 SIG Labs", font=("Arial", 14), fg="white", bg="#2D3E50", justify="left")
        self.result_label.pack(side=tk.BOTTOM, pady=5)
        
        # Load portfolio
        self.load_portfolio()

    def import_csv_threaded(self):
        """Runs the import_csv method in a separate thread."""
        threading.Thread(target=lambda: self.import_csv()).start()

 
 
    
    def import_csv(self):
        """Import stock data from the JStock CSV file and populate the portfolio."""
        import_file = "Buy Portfolio Management.csv"  # File name to import
        try:
            # Read the CSV file
            df = pd.read_csv(import_file)
    
            # Ensure required columns are present
            required_columns = ["Code", "Date", "Units", "Purchase Price"]
            if not all(col in df.columns for col in required_columns):
                messagebox.showerror("Error", "Missing required columns in CSV.")
                return
    
            # Extract and transform relevant data
            imported_data = []
            for _, row in df.iterrows():
                try:
                    stock_ticker = row["Code"]
                    date_purchased = pd.to_datetime(row["Date"]).strftime("%d-%m-%Y")  # Convert to DD-MM-YYYY
                    units_purchased = float(row["Units"])
                    purchase_price = float(row["Purchase Price"])
                    total_purchase_price = units_purchased * purchase_price
    
                    imported_data.append((stock_ticker, date_purchased, units_purchased, purchase_price, total_purchase_price))
                except Exception as e:
                    print(f"Error processing row: {row} -> {e}")
                    continue
    
            # Populate the Treeview
            for stock_data in imported_data:
                self.tree.insert("", "end", values=stock_data)
    
            # Save to portfolio file
            self.save_portfolio()
            messagebox.showinfo("Success", f"Imported {len(imported_data)} stocks successfully!")
    
            # Notify user and restart the program
            messagebox.showinfo("Restarting", "The program will now restart to apply changes.")
            
            # Restart the program in a new process
            python = sys.executable
            script = sys.argv[0]
    
            # Launch a new process to restart the program
            subprocess.Popen([python, script])
    
            # Kill the old process
            os.kill(os.getpid(), 9)  # Forcefully terminate the old process
    
        except FileNotFoundError:
            messagebox.showerror(
                "INFO",
                f"File '{import_file}' not found. Use JStock first to export the data into a Buy Portfolio Management.csv file and place it in the same dir as RiskTide, after this you can press import"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import CSV: {e}")
 

    def generate_graphs(self):
        """Generate and display various graphs for risk metrics."""
        try:
            # Load the metrics summary data
            df = pd.read_csv('stock_metrics_summary.csv')
    
            # Create a popup window for the graphs
            graph_window = tk.Toplevel(self.root)
            graph_window.title("Risk Metrics Graphs")
            graph_window.geometry("900x700")
            graph_window.grab_set()
            graph_window.iconbitmap('logo.ico')
    
            # Create a Canvas for scrollable content
            canvas = tk.Canvas(graph_window)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
            # Add a scrollbar
            scrollbar = tk.Scrollbar(graph_window, orient=tk.VERTICAL, command=canvas.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
            canvas.configure(yscrollcommand=scrollbar.set)
    
            # Create a frame inside the Canvas
            scrollable_frame = tk.Frame(canvas)
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    
            # Update the scrollable region dynamically
            def update_scroll_region(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
    
            scrollable_frame.bind("<Configure>", update_scroll_region)
    
            # Graph 1: Bar Chart (Sharpe Ratio)
            plt.figure(figsize=(8, 4))
            sns.barplot(x="Stock Ticker", y="Sharpe Ratio", data=df)
            plt.title("Sharpe Ratio by Stock")
            plt.xticks(rotation=45)
            plt.tight_layout()
            canvas_plot = FigureCanvasTkAgg(plt.gcf(), master=scrollable_frame)
            canvas_plot.draw()
            canvas_plot.get_tk_widget().pack(pady=10)
    
            # Graph 2: Pie Chart (Proportion of Max Drawdown)
            plt.figure(figsize=(6, 6))
            plt.pie(
                df["Max Drawdown"].abs(),
                labels=df["Stock Ticker"],
                autopct='%1.1f%%',
                startangle=140,
                colors=sns.color_palette("pastel"),
            )
            plt.title("Proportion of Max Drawdown")
            canvas_plot = FigureCanvasTkAgg(plt.gcf(), master=scrollable_frame)
            canvas_plot.draw()
            canvas_plot.get_tk_widget().pack(pady=10)
    
            # Graph 3: Scatter Plot (Alpha vs. Beta)
            plt.figure(figsize=(8, 5))
            sns.scatterplot(x="Alpha", y="Beta", data=df, hue="Stock Ticker", s=100, palette="viridis")
            plt.title("Alpha vs. Beta")
            plt.tight_layout()
            canvas_plot = FigureCanvasTkAgg(plt.gcf(), master=scrollable_frame)
            canvas_plot.draw()
            canvas_plot.get_tk_widget().pack(pady=10)
    
            # Graph 4: Box Plot (Distribution of Sharpe Ratios)
            plt.figure(figsize=(6, 4))
            sns.boxplot(y="Sharpe Ratio", data=df, color=sns.color_palette("Set2")[0])
            plt.title("Distribution of Sharpe Ratios")
            plt.tight_layout()
            canvas_plot = FigureCanvasTkAgg(plt.gcf(), master=scrollable_frame)
            canvas_plot.draw()
            canvas_plot.get_tk_widget().pack(pady=10)
    
            # Graph 5: Line Chart (Sample Trend - Simulate Cumulative Returns)
            cumulative_returns = (1 + df["Alpha"].fillna(0)).cumprod()
            plt.figure(figsize=(8, 4))
            plt.plot(df["Stock Ticker"], cumulative_returns, marker="o", linestyle="-", color="green")
            plt.title("Cumulative Returns (Simulated using Alpha)")
            plt.xlabel("Stock Ticker")
            plt.ylabel("Cumulative Returns")
            plt.tight_layout()
            canvas_plot = FigureCanvasTkAgg(plt.gcf(), master=scrollable_frame)
            canvas_plot.draw()
            canvas_plot.get_tk_widget().pack(pady=10)
    
            # Graph 6: Heatmap (Correlation Matrix)
            plt.figure(figsize=(8, 6))
    
            # Check if there is enough data for correlation matrix
            if df.shape[0] > 1:  # Ensure more than 1 row of data
                # Drop rows with NaN values in the selected columns
                df_clean = df.dropna(subset=["Alpha", "Beta", "Sharpe Ratio", "Sortino Ratio", "Omega Ratio"])
                
                if df_clean.shape[0] > 1:  # Check if enough rows remain
                    correlation_matrix = df_clean[["Alpha", "Beta", "Sharpe Ratio", "Sortino Ratio", "Omega Ratio"]].corr()
                    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", cbar=True)
                    plt.title("Correlation Matrix of Metrics")
                    plt.tight_layout()
                    canvas_plot = FigureCanvasTkAgg(plt.gcf(), master=scrollable_frame)
                    canvas_plot.draw()
                    canvas_plot.get_tk_widget().pack(pady=10)
                else:
                    messagebox.showwarning("INFO", "Not enough data for correlation matrix. Please add enough Portfolio data first or import and restart. Skipping...")
            else:
                messagebox.showwarning("INFO", "Not enough rows in the dataset for meaningful correlation. Please add enough Portfolio data first or import and restart. Skipping...")
    
            # Graph 7: Histogram (Frequency of Skewness)
            plt.figure(figsize=(8, 4))
            sns.histplot(df["Skewness"], kde=True, bins=10, color="purple")
            plt.title("Distribution of Skewness")
            plt.tight_layout()
            canvas_plot = FigureCanvasTkAgg(plt.gcf(), master=scrollable_frame)
            canvas_plot.draw()
            canvas_plot.get_tk_widget().pack(pady=10)
    
            def export_graphs():
                file_path = tk.filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
                if file_path:
                    pdf_pages = PdfPages(file_path)
                    for figure in plt.get_fignums():
                        pdf_pages.savefig(figure)
                    pdf_pages.close()
                    messagebox.showinfo("Success", "Graphs exported successfully!")
    
            export_button = tk.Button(scrollable_frame, text="Export Graphs", command=export_graphs, font=("Arial", 12), fg="white", bg="#4A90E2")
            export_button.pack(pady=10)
    
            # Add a Close button at the bottom
            close_button = tk.Button(scrollable_frame, text="Close", command=graph_window.destroy, font=("Arial", 12), fg="white", bg="#E94E77")
            close_button.pack(pady=20)
    
        except FileNotFoundError:
            messagebox.showerror("INFO", "Stock metrics summary file not found. Please add enough Portfolio data first or import.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate graphs: {e}")

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


     
    def calculate_risk_metrics_threaded(self):
        """Runs the calculate_risk_metrics method in a separate thread."""
        threading.Thread(target=lambda: self.calculate_risk_metrics()).start()

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
            metrics_modal.iconbitmap('logo.ico')  # Set the icon for the modal window
    
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
    
            # Add a frame for buttons
            button_frame = tk.Frame(metrics_modal, bg="#2D3E50")
            button_frame.pack(fill="x", pady=10)
    
            def export_metrics():
                file_path = tk.filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
                if file_path:
                    stock_metrics_df.to_csv(file_path, index=False)
                    messagebox.showinfo("Success", "Metrics exported successfully!")
    
            # Add an Export button
            export_button = tk.Button(button_frame, text="Export Metrics", font=("Arial", 12, "bold"), command=export_metrics, fg="white", bg="#4A90E2")
            export_button.pack(side=tk.LEFT, padx=10, pady=10)
    
            # Add a close button
            close_button = tk.Button(button_frame, text="Close", font=("Arial", 12, "bold"), command=metrics_modal.destroy, fg="white", bg="#E94E77")
            close_button.pack(side=tk.RIGHT, padx=10, pady=10)
    
        except FileNotFoundError:
            messagebox.showerror("INFO", "Please add data to the portfolio in order for the software to work.")
        except pd.errors.EmptyDataError:
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


        about_label = tk.Label(about_modal, text="RiskTide Portfolio Management v81.180 Patch 1\n\nDeveloped by Peter De Ceuster", font=("Arial", 16), fg="black")
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
        1. Add or Import stocks to your portfolio. (use Jstock and export Buy Portfolio Management.csv in the same dir as RiskTide and press import)
        2. Calculate your portfolio's risk metrics
        3. Delete entries from your portfolio
        4. View risk metrics in a detailed modal
        You may restart after adding entries for the graphs and metrics to load properly.
        
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
        
        The charts might help you analyze your investments.
        
        The graphs generated for your portfolio metrics provide valuable insights into the risk and performance of your investments. Below is a guide to understanding each graph:
        
        1. Bar Chart: Sharpe Ratio by Stock
        What it shows: The Sharpe Ratio measures the risk-adjusted return of each stock in your portfolio.
        How to interpret:
        Higher Sharpe Ratios (> 2) indicate better risk-adjusted performance.
        Ratios between 1 and 2 suggest acceptable returns for the risk taken.
        Ratios below 1 are generally undesirable and may indicate poor risk-return balance.
        2. Pie Chart: Proportion of Max Drawdown
        What it shows: The contribution of each stock to the portfolio's overall risk, represented by its maximum drawdown (largest loss from peak to trough).
        How to interpret:
        Larger slices indicate stocks that have significantly contributed to portfolio risk.
        Consider reducing exposure to stocks with a disproportionately large share if you're risk-averse.
        3. Scatter Plot: Alpha vs. Beta
        What it shows: The relationship between Alpha (excess return over a benchmark) and Beta (volatility compared to the market) for each stock.
        How to interpret:
        Stocks with high Alpha and low Beta are ideal, as they offer high returns with lower risk.
        High Alpha, high Beta suggests high returns but increased risk.
        Low Alpha, low Beta indicates safer investments with modest or poor returns.
        4. Box Plot: Distribution of Sharpe Ratios
        What it shows: The range and distribution of Sharpe Ratios across all stocks in your portfolio.
        How to interpret:
        Narrow box: Consistent risk-adjusted performance among stocks.
        Wide box or outliers: Indicates variability in risk-return profiles. Outliers may warrant a deeper look to understand their impact on the portfolio.
        5. Line Chart: Cumulative Returns (Simulated using Alpha)
        What it shows: A simulated trend of cumulative returns based on Alpha values for each stock.
        How to interpret:
        An upward trend indicates growing returns.
        A flat or declining trend suggests underperformance or stagnation.
        6. Heatmap: Correlation Matrix of Metrics
        What it shows: The correlation between key metrics (e.g., Alpha, Beta, Sharpe Ratio, Sortino Ratio, Omega Ratio) across your portfolio.
        How to interpret:
        Strong positive correlations (near +1) suggest metrics that move together.
        Strong negative correlations (near -1) highlight metrics with opposite trends.
        Weak correlations (near 0) indicate independent relationships, which can be useful for diversification.
        7. Histogram: Frequency of Skewness
        What it shows: The distribution of skewness (asymmetry in returns) across your portfolio.
        How to interpret:
        Positive skewness suggests the potential for large gains.
        Negative skewness implies a higher probability of large losses.
        A centered distribution (close to 0 skewness) indicates balanced risk and reward.
        By analyzing these graphs, you can make more informed decisions about which stocks to hold, sell, or monitor closely based on their performance and risk characteristics.        
        
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
