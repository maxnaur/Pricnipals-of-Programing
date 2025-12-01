import customtkinter as ctk
from cripto_search import fetch_crypto_list, search_crypto

class set_Up_Buy():
    def __init__(self, Menu):
        """set up the list available cryptocurrencies GUI"""
        self.Menu = Menu
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
        print(f"Selected coin: {coin['name']} ({coin['symbol'].upper()})")
        self.clear_frame()
        self.Menu.pack_forget()
        self.Menu.pack(fill='both', expand=True)
        
        ctk.CTkLabel(
            self.Menu,
            text='Buy Cryptocurrency',
            font=ctk.CTkFont(family='Consolas', size=15)
        ).pack(pady=14)
        
        ctk.CTkLabel(
            self.Menu,
            text=f'You have selected: {coin["name"]} ({coin["symbol"].upper()})',
            font=ctk.CTkFont(family='Consolas', size=12)
        ).pack(pady=14)

        






    def clear_frame(self):
        self.list_frame.pack_forget()
        # Remove any previous buttons/widgets so we don't accumulate duplicates
        for child in self.list_frame.winfo_children():
            child.destroy()
        self.list_frame.pack(fill="both", expand=True)