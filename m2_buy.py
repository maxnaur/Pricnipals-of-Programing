import customtkinter as ctk
from cripto_search import fetch_crypto_list, search_crypto
from m2_database_interactions import database_connect
from CTkMessagebox import CTkMessagebox
import requests
from datetime import datetime

# Optional plotting support. If matplotlib is not installed we'll still show details
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False

class set_Up_Buy():
    def __init__(self, Menu, dbLocation, userID):
        """set up the list available cryptocurrencies GUI"""
        self.Menu = Menu
        self.dbLocation = dbLocation
        self.userID = userID
        self.setup_Surch_GUI()

    def setup_Surch_GUI(self):
        # {'id': 'bitcoin', 'symbol': 'btc', 'name': 'Bitcoin', 'image': 'https://coin-images.coingecko.com/coins/images/1/large/bitcoin.png?1696501400', 'current_price': 63984, 'market_cap': 1276453073946, 'market_cap_rank': 1, 'fully_diluted_valuation': 1276503042862, 'total_volume': 59489755665, 'high_24h': 65208, 'low_24h': 63187, 'price_change_24h': 224.42, 'price_change_percentage_24h': 0.35198, 'market_cap_change_24h': 5743695879, 'market_cap_change_percentage_24h': 0.45201, 'circulating_supply': 19950600.0, 'total_supply': 19951381.0, 'max_supply': 21000000.0, 'ath': 93529, 'ath_change_percentage': -31.45666, 'ath_date': '2025-10-06T18:57:42.558Z', 'atl': 43.9, 'atl_change_percentage': 145923.68481, 'atl_date': '2013-07-05T00:00:00.000Z', 'roi': None, 'last_updated': '2025-11-22T13:34:00.574Z'}
        self.search_entry = ctk.CTkEntry(self.Menu, width=350, placeholder_text="Search crypto...")
        # Bind Enter to call fetch_search_crypto; bind handlers receive an event argument
        self.search_entry.bind("<Return>", lambda event: self.fetch_search_crypto())
        self.search_entry.pack(pady=10)
        self.search_button = ctk.CTkButton(self.Menu, text="Search", command=self.fetch_search_crypto)
        self.search_button.pack(pady=5)

        self.container = ctk.CTkFrame(self.Menu)
        self.container.pack(padx=10, pady=10, fill="both", expand=True)
        self.list_frame = ctk.CTkScrollableFrame(self.container)
        self.list_frame.pack(fill="both", expand=True)
        self.fetch_default_crypto_data()

    # API calls
    def fetch_default_crypto_data(self): # Fetch top 250 cryptos by market cap
        response = fetch_crypto_list()
        self.display_crypto_list(response)
    
    def fetch_search_crypto(self): # Search for specific crypto
        term = self.search_entry.get()
        response = search_crypto(term)
        # The search endpoint returns a dict with a 'coins' list; normalize to a list
        if isinstance(response, dict):
            crypto_list = response.get('coins') or response.get('data') or []
        else:
            crypto_list = response
        self.display_crypto_list(crypto_list)

    # make the display list and search function
    def display_crypto_list(self, crypto_data):
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
        # Determine coin id and name
        if isinstance(coin, dict):
            self.coin_id = coin.get('id') or coin.get('symbol') or coin.get('name')
            self.coin_name = coin.get('name') or str(self.coin_id)
        else:
            self.coin_id = str(coin)
            self.coin_name = self.coin_id

        # Fetch details and price history
        self.details = self.fetch_coin_details(self.coin_id)
        history = self.fetch_price_history(self.coin_id, days=365)

        # Clear previous content
        self.clear_frame()
        self.Menu.pack_forget()
        
        # Info section
        info_frame = ctk.CTkFrame(self.Menu)
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
        Make_Label(f"Coin ID: {self.coin_id}")
        Make_Label(f"Name: {self.coin_name}")
        Make_Label(f"Current price (GBP): £{self.current_price:,}" if self.current_price is not None else "Price: N/A")
        Make_Label(f"Market cap (GBP): £{int(market_cap):,}" if market_cap else "Market cap: N/A")
        Make_Label(f"24h change: {change_24h:.2f}%" if change_24h is not None else "24h change: N/A")
        
        # Purchase section
        buy_frame = ctk.CTkFrame(self.Menu)
        buy_frame.pack(fill='x', padx=12, pady=8)
        ctk.CTkLabel(buy_frame, text="Amount to buy (in GBP):").pack(side='left', padx=(0,6))
        self.amount_entry = ctk.CTkEntry(buy_frame, width=160)
        self.amount_entry.pack(side='left')

        ctk.CTkButton(buy_frame, text="Buy", command=self.send_buy).pack(side='left', padx=8)

        # Chart area
        chart_frame = ctk.CTkFrame(self.Menu)
        chart_frame.pack(fill='both', expand=True, padx=12, pady=8)

        if history and MATPLOTLIB_AVAILABLE:
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
        elif history and not MATPLOTLIB_AVAILABLE:
            ctk.CTkLabel(chart_frame, text="matplotlib not installed — install it to see the price chart").pack(pady=20)
        else:
            ctk.CTkLabel(chart_frame, text="No historical price data available").pack(pady=20)

    # genteral utility to clear the main frame
    def clear_frame(self):
        self.list_frame.pack_forget()
        # Remove any previous buttons/widgets so we don't accumulate duplicates
        for child in self.list_frame.winfo_children():
            child.destroy()
        self.list_frame.pack(fill="both", expand=True)

    # ------------------------- Interact with API -------------------------
    def fetch_coin_details(self, coin_id):
        """Fetch coin details (market data) from CoinGecko."""
        try:
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
            params = {
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'true',
                'community_data': 'false',
                'developer_data': 'false',
                'sparkline': 'false'
            }
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception:
            return None

    def fetch_price_history(self, coin_id, days=365):
        """Fetch market chart (prices) for the coin in GBP for the last `days` days."""
        try:
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
            params = {'vs_currency': 'gbp', 'days': days, 'interval': 'daily'}
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
            return data.get('prices')
        except Exception:
            return None

    def send_buy(self):
        val = self.amount_entry.get().strip()
        try:
            amount = float(val)
        except Exception:
            CTkMessagebox(title="Error", message="Enter a valid number", icon="cancel")
            return
        
        coin_amount = amount / self.current_price
        if coin_amount <= 0:
            CTkMessagebox(title="Error", message="Enter a positive amount", icon="cancel")
            return

        # interact with database
        db = database_connect(self.dbLocation)
        db.add_crypto_to_wallet(self.userID, self.coin_id, coin_amount)
        db.close()
        
        CTkMessagebox(
            title="Purchase", 
            message=f"You have baught £{amount:.2f} of {self.coin_name} (~{coin_amount:.6f} {self.details.get('symbol','')})", 
            icon="check")
        
        # resset
        self.clear_frame()
        self.setup_Surch_GUI()