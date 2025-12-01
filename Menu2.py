import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import requests
import os
from m2_database_interactions import database_connect
from m2_qr_code import Display_QR_code

from m2_buy import set_Up_Buy

class Wallet_Sidebar:
    def __init__(self, main, dbLocation, username):
        """Initialize the wallet sidebar."""
        self.main = main
        self.main.geometry('1000x800')
        self.sidebar = ctk.CTkFrame(self.main, width=120, fg_color="gray30")
        self.sidebar.pack(side='left', fill='y')
        self.dbLocation = dbLocation
        self.username = username
        self.Menu = None

        # Database connection
        self.db = database_connect(self.dbLocation)
        self.userID = self.db.get_userID(username)
        self.holdings = self.db.get_userWallet(self.userID)
        self.db.close()

        self.Setup_sidebar()


    # ------------------------- Sidebar Setup -------------------------
    def Setup_sidebar(self):
        """Set up sidebar buttons and layout."""
        self.sidebar.Crypto_Lb = ctk.CTkLabel(
            self.sidebar,
            text=f"Crypto Menu\n{self.username}",
            font=ctk.CTkFont(family='Consolas', size=12)
        )
        self.sidebar.Crypto_Lb.pack(fill="x", pady=5)

        def create_button(text):
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=lambda: self.Load_Menu(text)
            )
            btn.pack(fill="x", pady=5)

        create_button("Home")
        create_button("Wallet")
        create_button("Buy")
        create_button("Transfer")
        create_button("QR Code\nof userID")

        self.Menu = ctk.CTkFrame(self.main, fg_color="gray25")
        self.Menu.pack(fill='both', expand=True)
        self.Load_Menu("Home")

    # ------------------------- Menu Switching -------------------------
    def Load_Menu(self, menu_name):
        """Switch between menus."""
        if self.Menu:
            self.Menu.pack_forget()

        self.Menu = ctk.CTkFrame(self.main)
        self.Menu.pack(fill='both', expand=True)

        if menu_name == "Home":
            self.load_HomeGUI()
        elif menu_name == "Wallet":
            self.load_WalletGUI()
        elif menu_name == "Buy":
            buy = set_Up_Buy(self.Menu, self.dbLocation, self.userID)
            #self.load_BuyGUI()
        elif menu_name == "Transfer":
            self.load_TransferGUI()
        elif menu_name == "QR Code\nof userID":
            Display_QR_code(self)
    
    # ------------------------- Home GUI -------------------------
    def load_HomeGUI(self):
        ctk.CTkLabel(
            self.Menu,
            text='Home Page',
            font=ctk.CTkFont(family='Consolas', size=15)
        ).pack(pady=14)

        ctk.CTkLabel(
            self.Menu,
            text=f'Hello {self.username}',
            font=ctk.CTkFont(family='Consolas', size=15)
        ).pack(pady=14)

    # ------------------------- Wallet GUI -------------------------
    def load_WalletGUI(self):
        ctk.CTkLabel(
            self.Menu,
            text="Wallet Page",
            font=ctk.CTkFont(family='Consolas', size=15)
        ).pack(pady=14)

        if not self.holdings:
            CTkMessagebox(title="Info", message="No holdings found", icon="info")
        else:
            crypto_id, amount = self.holdings
            ctk.CTkLabel(
                self.Menu,
                text=f"Crypto ID: {crypto_id} | Amount: {amount}",
                font=ctk.CTkFont(size=12)
            ).pack(pady=10)

    # ------------------------- Buy GUI -------------------------
    def load_BuyGUI(self):
        """ctk.CTkLabel(
            self.Menu,
            text="Buy User",
            font=ctk.CTkFont(family='Consolas', size=15)
        ).pack(pady=14)"""
        self.list_available_cryptocurrencies()
    
    def list_available_cryptocurrencies(self):
        # API calls
        def fetch_default_crypto_data(): # Fetch top 250 cryptos by market cap
            url = r"https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "gbp", # pound
                "include_market_cap": "true", # include market cap data
                "order": "market_cap_desc", # order by market cap
                "per_page": 250, # number of results
            }
            
            response = requests.get(url, params)
            assert response.status_code == 200, "API request failed" # error handling
            display_crypto_list(response.json())
        
        def search_crypto(): # Search for specific crypto
            url = r"https://api.coingecko.com/api/v3/search"
            term = search_entry.get()
            params = {"query": term} # search term
            response = requests.get(url, params)
            assert response.status_code == 200, "API request failed" # error handling
            display_crypto_list(response.json())

        # make the display list and search function
        def display_crypto_list(crypto_data):
            list_frame.pack_forget()
            for coin in crypto_data:
                name = f"{coin['name'].ljust(65)} {f"({coin['symbol'].upper()})".rjust(18)} - Market Cap: £{coin['market_cap']:,}"
                btn = ctk.CTkButton(
                    list_frame,
                    text=name,
                    font=('Consolas', 12),
                    anchor="w",
                    fg_color="transparent",
                    hover_color="#494545",
                    command=lambda n=name: label.configure(text=f"Selected: {n}")
                ).pack(fill="x", padx=6, pady=3)


        # {'id': 'bitcoin', 'symbol': 'btc', 'name': 'Bitcoin', 'image': 'https://coin-images.coingecko.com/coins/images/1/large/bitcoin.png?1696501400', 'current_price': 63984, 'market_cap': 1276453073946, 'market_cap_rank': 1, 'fully_diluted_valuation': 1276503042862, 'total_volume': 59489755665, 'high_24h': 65208, 'low_24h': 63187, 'price_change_24h': 224.42, 'price_change_percentage_24h': 0.35198, 'market_cap_change_24h': 5743695879, 'market_cap_change_percentage_24h': 0.45201, 'circulating_supply': 19950600.0, 'total_supply': 19951381.0, 'max_supply': 21000000.0, 'ath': 93529, 'ath_change_percentage': -31.45666, 'ath_date': '2025-10-06T18:57:42.558Z', 'atl': 43.9, 'atl_change_percentage': 145923.68481, 'atl_date': '2013-07-05T00:00:00.000Z', 'roi': None, 'last_updated': '2025-11-22T13:34:00.574Z'}
        search_entry = ctk.CTkEntry(self.Menu, width=350, placeholder_text="Search crypto...")
        search_entry.bind("<Return>", search_crypto)
        search_entry.pack(pady=10)
        search_button = ctk.CTkButton(self.Menu, text="Search", command=search_crypto).pack(pady=5)

        container = ctk.CTkFrame(self.Menu)
        container.pack(padx=10, pady=10, fill="both", expand=True)
        list_frame = ctk.CTkScrollableFrame(container)
        list_frame.pack(fill="both", expand=True)
        label = ctk.CTkLabel(container, text="Selected: None", font=ctk.CTkFont(size=14)).pack(pady=14)
        fetch_default_crypto_data()

        # make the display list and search function





        
    # ------------------------- Transfer GUI -------------------------
    def load_TransferGUI(self):
        ctk.CTkLabel(
            self.Menu,
            text="Transfer User",
            font=ctk.CTkFont(family='Consolas', size=15)
        ).pack(pady=14)


if __name__ == "__main__":
        dbLocation = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Database.db')
        
        # GUI setup
        ctk.set_appearance_mode("Dark")  # Dark mode only
        ctk.set_default_color_theme("dark-blue")

        GUI = ctk.CTk()
        GUI.title('Crypto Wallet')
        GUI.geometry('500x400')

        # Sidebar setup (make sure Login_Sidebar uses CTk widgets)
        trigger = Wallet_Sidebar(GUI, dbLocation, "admin")
        trigger.main.mainloop()