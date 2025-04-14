import tkinter as tk
from tkinter import font
import yfinance as yf
import json
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Fake account balance
balance = 10000.0
shares_owned = 0
current_price = 0.0
stock_symbol = ""
portfolio_file = "portfolio.json"
portfolio = {}

# Initialize window
root = tk.Tk()
root.title("NeoBrutalist Paper Trading")
root.attributes('-fullscreen', True)
root.configure(bg="#e5e5e5")

# Fonts
heading_font = font.Font(family="Montserrat", size=16, weight="bold")
content_font = font.Font(family="Montserrat", size=12, weight="bold")

# Shadow and Card
shadow = tk.Frame(root, bg="black")
shadow.place(relx=0.06, rely=0.06, relwidth=0.88, relheight=0.82)

card = tk.Frame(root, bg="#161179", highlightbackground="black", highlightthickness=2)
card.place(relx=0.05, rely=0.05, relwidth=0.88, relheight=0.82)

# Header
header = tk.Frame(card, bg="white", height=50)
header.pack(fill='x')
tk.Label(header, text="Paper Stock Trader", bg="white", fg="#261FB3", font=heading_font).pack(anchor="w", padx=20, pady=10)

# Split layout
top_panel = tk.Frame(card, bg="#161179")
top_panel.pack(fill='x', padx=20, pady=(10, 0))

bottom_panel = tk.Frame(card, bg="#161179")
bottom_panel.pack(fill='both', expand=True, padx=20, pady=10)

chart_frame = tk.Frame(top_panel, bg="#ffffff", relief="ridge", borderwidth=2, width=260, height=180)
chart_frame.grid(row=0, column=3, rowspan=4, padx=(30, 0), sticky="ne")
chart_frame.grid_propagate(False)

chart_canvas = None

# Labels & Entry
balance_label = tk.Label(top_panel, text=f"Balance: ${balance:.2f}", bg="#161179", fg="#FBE4D6", font=content_font)
balance_label.grid(row=0, column=0, sticky="w", pady=2)

price_label = tk.Label(top_panel, text="Price: $0.00", bg="#161179", fg="#FBE4D6", font=content_font)
price_label.grid(row=1, column=0, sticky="w", pady=2)

shares_label = tk.Label(top_panel, text=f"Shares Owned: {shares_owned}", bg="#161179", fg="#FBE4D6", font=content_font)
shares_label.grid(row=2, column=0, sticky="w", pady=2)

tk.Label(top_panel, text="Enter Stock Symbol:", bg="#161179", fg="#FBE4D6", font=content_font).grid(row=0, column=1, sticky="e", padx=10)
symbol_entry = tk.Entry(top_panel, font=content_font)
symbol_entry.grid(row=0, column=2, sticky="w", pady=2)

tk.Label(top_panel, text="Enter Number of Shares:", bg="#161179", fg="#FBE4D6", font=content_font).grid(row=1, column=1, sticky="e", padx=10)
shares_entry = tk.Entry(top_panel, font=content_font)
shares_entry.insert(0, "1")
shares_entry.grid(row=1, column=2, sticky="w", pady=2)

# Buttons Row
button_frame = tk.Frame(top_panel, bg="#161179")
button_frame.grid(row=3, column=0, columnspan=3, sticky="w", pady=10)

tk.Button(button_frame, text="Fetch Price", command=lambda: fetch_price(), bg="#261FB3", fg="#FBE4D6", font=content_font, relief="flat", borderwidth=4).pack(side="left", padx=5)
tk.Button(button_frame, text="Buy Shares", command=lambda: buy_stock(), bg="#261FB3", fg="#FBE4D6", font=content_font, relief="flat", borderwidth=4).pack(side="left", padx=5)
tk.Button(button_frame, text="Sell Shares", command=lambda: sell_stock(), bg="#261FB3", fg="#FBE4D6", font=content_font, relief="flat", borderwidth=4).pack(side="left", padx=5)
tk.Button(button_frame, text="Save Portfolio", command=lambda: save_portfolio(), bg="#261FB3", fg="#FBE4D6", font=content_font, relief="flat", borderwidth=4).pack(side="left", padx=5)
tk.Button(button_frame, text="Load Portfolio", command=lambda: load_portfolio(), bg="#261FB3", fg="#FBE4D6", font=content_font, relief="flat", borderwidth=4).pack(side="left", padx=5)
tk.Button(button_frame, text="Fetch Stock Chart", command=lambda: fetch_chart(), bg="#261FB3", fg="#FBE4D6", font=content_font, relief="flat", borderwidth=4).pack(side="left", padx=5)

# History Panel
tk.Label(bottom_panel, text="Transaction History:", bg="#161179", fg="#FBE4D6", font=content_font).pack(anchor="nw")

history_frame = tk.Frame(bottom_panel, bg="#161179")
history_frame.pack(fill="both", expand=True, pady=(5, 10))

history_scrollbar = tk.Scrollbar(history_frame)
history_scrollbar.pack(side="right", fill="y")

history_text = tk.Text(history_frame, font=("Courier", 10), bg="white", fg="black", yscrollcommand=history_scrollbar.set)
history_text.pack(side="left", fill="both", expand=True)
history_scrollbar.config(command=history_text.yview)

# Logic Functions
def fetch_price():
    global current_price, stock_symbol
    stock_symbol = symbol_entry.get().strip().upper()
    if not stock_symbol:
        return
    try:
        ticker = yf.Ticker(stock_symbol)
        data = ticker.history(period="1d")
        current_price = data['Close'].iloc[-1]
        price_label.config(text=f"Price: ${current_price:.2f}")
        print(f"Fetched {stock_symbol} price: ${current_price:.2f}")
    except Exception as e:
        price_label.config(text="Price: Error fetching data")
        print(f"Error: {e}")

def buy_stock():
    global balance, portfolio
    try:
        symbol = symbol_entry.get().strip().upper()
        num = int(shares_entry.get())
        cost = current_price * num
        if current_price > 0 and balance >= cost:
            balance -= cost
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if symbol in portfolio:
                portfolio[symbol]["shares"] += num
            else:
                portfolio[symbol] = {"shares": num, "price": current_price, "timestamp": timestamp}
            update_labels()
            print(f"Bought {num} share(s) of {symbol} at ${current_price:.2f}")
            log_transaction(f"📈 Bought {num} share(s) of {symbol} at ${current_price:.2f} on {timestamp}")
        else:
            print("Not enough balance or invalid price.")
    except ValueError:
        print("Enter a valid number of shares.")


def sell_stock():
    global balance, portfolio
    try:
        symbol = symbol_entry.get().strip().upper()
        num = int(shares_entry.get())
        if symbol in portfolio and portfolio[symbol]["shares"] >= num and current_price > 0:
            balance += current_price * num
            portfolio[symbol]["shares"] -= num
            if portfolio[symbol]["shares"] == 0:
                del portfolio[symbol]
            update_labels()
            print(f"Sold {num} share(s) of {symbol} at ${current_price:.2f}")
            log_transaction(f"📉 Sold {num} share(s) of {symbol} at ${current_price:.2f}")
        else:
            print("Not enough shares or invalid price.")
    except ValueError:
        print("Enter a valid number of shares.")

def save_portfolio():
    data = {
        "balance": balance,
        "portfolio": portfolio
    }
    with open(portfolio_file, "w") as f:
        json.dump(data, f, indent=4)
    log_transaction("💾 Portfolio saved.")


def load_portfolio():
    global balance, portfolio
    try:
        with open(portfolio_file, "r") as f:
            data = json.load(f)
            balance = data["balance"]
            portfolio = data["portfolio"]
            update_labels()
            log_transaction("📂 Portfolio loaded.")
            show_portfolio()
    except FileNotFoundError:
        log_transaction("❌ No saved portfolio found.")

def log_transaction(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history_text.insert(tk.END, f"[{timestamp}] {message}\n")
    history_text.see(tk.END)

def fetch_chart():
    global chart_canvas
    symbol = symbol_entry.get().strip().upper()
    if not symbol:
        log_transaction("⚠️ Enter a stock symbol to fetch chart.")
        return
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1mo")  # 1 month data
        if data.empty:
            log_transaction("⚠️ No chart data available.")
            return

        # Remove previous chart
        if chart_canvas:
            chart_canvas.get_tk_widget().destroy()

        # Create a small figure; size doesn’t matter much since we’ll pack it to fill
        fig = Figure(figsize=(2.6, 1.4), dpi=100)  # slightly smaller
        ax = fig.add_subplot(111)
        ax.plot(data.index, data["Close"], color="blue")
        ax.set_title(f"{symbol} Price (1M)", fontsize=7)
        ax.set_xlabel("Date", fontsize=5)
        ax.set_ylabel("Price ($)", fontsize=5)
        ax.tick_params(axis='x', labelsize=5)
        ax.tick_params(axis='y', labelsize=5)
        fig.tight_layout()


        chart_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        chart_widget = chart_canvas.get_tk_widget()
        chart_widget.pack(fill="both", expand=True)
        chart_canvas.draw()

        log_transaction(f"📊 Fetched 1-month chart for {symbol}.")
    except Exception as e:
        log_transaction("❌ Failed to fetch chart.")
        print("Chart Error:", e)

def create_button_with_shadow(parent, text, command, bg_color):
    shadow = tk.Frame(parent, bg="black", bd=0)
    shadow.pack(side="left", padx=(6, 0), pady=(6, 0))

    button_wrapper = tk.Frame(shadow, bg="black")
    button_wrapper.pack(padx=(0, 2), pady=(0, 2))

    button = tk.Button(button_wrapper, 
                       text=text, 
                       command=command, 
                       bg=bg_color, 
                       fg="#FBE4D6", 
                       font=content_font, 
                       relief="flat", 
                       borderwidth=4,
                       highlightthickness=2,
                       highlightbackground="black")
    button.pack()

def show_portfolio():
    if not portfolio:
        log_transaction("📭 No stocks in portfolio.")
        return
    log_transaction("📋 Current Portfolio:")
    for symbol, details in portfolio.items():
        log_transaction(f"🔹 {symbol} — {details['shares']} share(s) bought at ${details['price']:.2f} on {details['timestamp']}")

def update_labels():
    total_shares = sum(stock["shares"] for stock in portfolio.values())
    shares_label.config(text=f"Shares Owned: {total_shares}")
    balance_label.config(text=f"Balance: ${balance:.2f}")

# Exit on Esc
root.bind("<Escape>", lambda e: root.destroy())
root.mainloop()
