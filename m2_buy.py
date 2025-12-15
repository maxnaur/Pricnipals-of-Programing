import customtkinter as ctk
from m2_database_interactions import database_connect
from CTkMessagebox import CTkMessagebox
import requests
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class set_Up_Buy():
    """create GUI for perchasing with the top 250 option by market cap"""
    def __init__(self, Menu, dbLocation, API_Search, userID):
        """set up the list available cryptocurrencies GUI"""
        self.Menu = Menu
        self.dbLocation = dbLocation
        self.userID = userID
        self.API_Search = API_Search
        self.Display = ctk.CTkFrame(self.Menu)
        self.Display.pack(fill='both', expand=True)
        self.setup_Search_GUI()

    def setup_Search_GUI(self):
        """set up search bar the the data"""
        self.search_entry = ctk.CTkEntry(self.Display, width=350, placeholder_text="Search crypto...")
        # Bind Enter to call fetch_search_crypto; bind handlers receive an event argument
        self.search_entry.bind("<Return>", lambda event: self.fetch_search_crypto())
        self.search_entry.pack(pady=10)
        self.search_button = ctk.CTkButton(self.Display, text="Search", command=self.fetch_search_crypto)
        self.search_button.pack(pady=5)

        self.container = ctk.CTkFrame(self.Display)
        self.container.pack(padx=10, pady=10, fill="both", expand=True)
        self.list_frame = ctk.CTkScrollableFrame(self.container)
        self.list_frame.pack(fill="both", expand=True)
        self.fetch_top_crypto_currencys()

    # API calls
    def fetch_top_crypto_currencys(self): 
        """Fetch top 250 cryptos by market cap"""
        response = self.API_Search.fetch_top_250_crypto_list()
        self.display_crypto_list(response)
    
    def fetch_search_crypto(self): 
        """Search for specific crypto"""
        term = self.search_entry.get()
        response = self.API_Search.search_coins(term)
        # The search endpoint returns a dict with a 'coins' list; normalize to a list
        if isinstance(response, dict):
            crypto_list = response.get('coins') or response.get('data') or []
        else:
            crypto_list = response
        self.display_crypto_list(crypto_list)


    def display_crypto_list(self, crypto_data):
        """make the display list and search function"""
        self.clear_frame()

        for coin in crypto_data:
            # Support both dict-like coin objects and other fallback formats
            name_display = coin.get('name') or coin.get('id') or '<unknown>'
            symbol_display = (coin.get('symbol') or '').upper()
            market_cap = coin.get('market_cap') or coin.get('market_cap_rank') or 0

            # Build a stable, readable label
            symbol_part = f" ({symbol_display})" if symbol_display else ''
            name = f"{name_display}{symbol_part} - Market Cap: £{int(market_cap):,}"

            btn = ctk.CTkButton(
                self.list_frame,
                text=name,
                font=('Consolas', 12),
                anchor="w",
                fg_color="transparent",
                hover_color="#494545",
            )
            # Attach coin data to the button widget
            btn.coin = coin
            # Capture the coin value for the command callback
            btn.configure(command=lambda c=coin: self.sellect_coin(c))
            btn.pack(fill="x", padx=6, pady=3)
            

    def sellect_coin(self, coin):
        """display seached cryto currency with its market data"""
        # Determine coin id and name
        if isinstance(coin, dict):
            self.coin_ID = coin.get('id') or coin.get('symbol') or coin.get('name')
            self.coin_name = coin.get('name') or str(self.coin_ID)
        else:
            self.coin_ID = str(coin)
            self.coin_name = self.coin_ID

        # Fetch details and price history
        self.details = self.API_Search.fetch_single_coin_details(self.coin_ID)
        history = self.API_Search.fetch_year_coin_history(self.coin_ID)

        # Clear previous content
        self.Display_resset()
        
        # Info section
        info_frame = ctk.CTkFrame(self.Display)
        info_frame.pack(fill='x', padx=12, pady=8)

        if self.details is None:
            ctk.CTkLabel(info_frame, text=f"No details found for {self.coin_name}").pack(pady=8)
            return

        market = self.details.get('market_data', {})
        self.current_price = market.get('current_price', {}).get('gbp')
        market_cap = market.get('market_cap', {}).get('gbp')
        change_24h = market.get('price_change_percentage_24h')

        def Make_Label(text):
            ctk.CTkLabel(
                info_frame, 
                text=text, 
                font=ctk.CTkFont(family='Consolas', size=12)
                ).pack(anchor='w')
        Make_Label(f"Coin ID: {self.coin_ID}")
        Make_Label(f"Name: {self.coin_name}")
        Make_Label(f"Current price (GBP): £{self.current_price:,}" if self.current_price is not None else "Price: N/A")
        Make_Label(f"Market cap (GBP): £{int(market_cap):,}" if market_cap else "Market cap: N/A")
        Make_Label(f"24h change: {change_24h:.2f}%" if change_24h is not None else "24h change: N/A")
        
        # Purchase section
        buy_frame = ctk.CTkFrame(self.Display)
        buy_frame.pack(fill='x', padx=12, pady=8)
        ctk.CTkLabel(buy_frame, text=f"Amount to buy ({self.coin_ID.upper()}):").pack(side='left', padx=(0,6))
        self.amount_entry = ctk.CTkEntry(buy_frame, width=160)
        self.amount_entry.pack(side='left')

        ctk.CTkButton(buy_frame, text="Buy", command=self.send_buy).pack(side='left', padx=8)

        # Chart area
        chart_frame = ctk.CTkFrame(self.Display)
        chart_frame.pack(fill='both', expand=True, padx=12, pady=8)

        if history:
            times = [datetime.fromtimestamp(p[0]/1000.0) for p in history]
            prices = [p[1] for p in history]

            fig = Figure(figsize=(8,4), dpi=100)
            ax = fig.add_subplot(111)
            ax.plot(times, prices, '-', linewidth=1)
            ax.set_title(f"{self.coin_name} price — last 12 months")
            ax.set_xlabel('Date')
            ax.set_ylabel('Price (GBP)')
            fig.autofmt_xdate()

            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
        else:
            ctk.CTkLabel(chart_frame, text="No historical price data available").pack(pady=20)

    # genteral utility to clear the main frame
    def clear_frame(self):
        self.list_frame.pack_forget()
        # Remove any previous buttons/widgets so we don't accumulate duplicates
        for child in self.list_frame.winfo_children():
            child.destroy()
        self.list_frame.pack(fill="both", expand=True)


    def send_buy(self):
        """interact with the database to perchase the crypto and add it to the wallet"""
        val = self.amount_entry.get().strip()
        try:
            coin_amount = float(val)
        except Exception:
            CTkMessagebox(title="Error", message="Enter a valid number", icon="cancel")
            return
        
        if coin_amount <= 0:
            CTkMessagebox(title="Error", message="Enter a positive amount", icon="cancel")
            return

        # Calculate GBP cost
        amount_gbp = coin_amount * self.current_price

        # interact with database
        db = database_connect(self.dbLocation)
        db.add_crypto_to_wallet(self.API_Search, self.userID, self.coin_ID, self.coin_name, coin_amount)
        db.Transaction_Buy(self.coin_ID, self.userID, coin_amount)
        db.close()
        
        CTkMessagebox(
            title="Purchase", 
            message=f"You have bought {coin_amount:.2f} {self.coin_ID.upper()} for £{amount_gbp:.2f}", 
            icon="check")
        
        # resset
        self.Display_resset()
        self.setup_Search_GUI()

    def Display_resset(self):
        """Resset everything"""
        self.Display.pack_forget()
        self.Display = ctk.CTkFrame(self.Menu)
        self.Display.pack(fill='both', expand=True)
    