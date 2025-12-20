import customtkinter as ctk
from m2_database_interactions import database_connect

class set_Up_Wallet:
    """Display User wallet GUI"""
    def __init__(self, Menu, dbLocation, API_search, userID):
        """set up GUI"""
        self.Menu = Menu
        self.dbLocation = dbLocation
        self.API_search = API_search
        self.userID = userID
        self.display_wallet()

    def display_wallet(self):
        """Display all cryptocurrencies owned by the user with their values."""
        # Create header
        ctk.CTkLabel(
            self.Menu,
            text="Your Wallet",
            font=ctk.CTkFont(family='Consolas', size=15)
        ).pack(pady=14)

        # Fetch wallet data
        db = database_connect(self.dbLocation)
        
        # Get all cryptos in wallet
        Wallet = db.get_userWallet(self.userID)
        db.close()

        if not Wallet:
            ctk.CTkLabel(
                self.Menu,
                text="No cryptocurrencies in your wallet",
                font=ctk.CTkFont(family='Consolas', size=12)
            ).pack(pady=10)
            return

        # Create scrollable frame for holdings
        container = ctk.CTkFrame(self.Menu)
        container.pack(padx=10, pady=10, fill="both", expand=True)
        
        scrollable_frame = ctk.CTkScrollableFrame(container)
        scrollable_frame.pack(fill="both", expand=True)

        total_value = 0

        # find names of all crypto currensy's
        Coin_IDs = [row[0] for row in Wallet]
        coins_details = self.API_search.fetch_crypto_batch(Coin_IDs)
        if not isinstance(coins_details, dict):
            coins_details = {}

        for Coin_ID, Coin_Name, amount in Wallet:
            # Fetch current price
            try:
                temp1 = coins_details.get(Coin_ID, {})
                price_gbp = temp1.get('current_price', 0)
            except Exception:
                price_gbp = 0
            
            coin_value = amount * price_gbp
            total_value += coin_value

            # Display individual holding
            holding_frame = ctk.CTkFrame(scrollable_frame, fg_color="gray30")
            holding_frame.pack(fill="x", padx=5, pady=5)

            ctk.CTkLabel(
                holding_frame,
                text=f"{Coin_Name} ({Coin_ID.upper()})",
                font=ctk.CTkFont(family='Consolas', size=12, weight="bold")
            ).pack(anchor="w", padx=10, pady=(5, 2))

            ctk.CTkLabel(
                holding_frame,
                text=f"Amount: {amount:.2f}",
                font=ctk.CTkFont(family='Consolas', size=11)
            ).pack(anchor="w", padx=10)

            ctk.CTkLabel(
                holding_frame,
                text=f"Price per coin: £{price_gbp:,.2f}",
                font=ctk.CTkFont(family='Consolas', size=11)
            ).pack(anchor="w", padx=10)

            ctk.CTkLabel(
                holding_frame,
                text=f"Total value: £{coin_value:,.2f}",
                font=ctk.CTkFont(family='Consolas', size=11, weight="bold"),
                text_color="lightgreen"
            ).pack(anchor="w", padx=10, pady=(2, 5))

        # Display total
        total_frame = ctk.CTkFrame(self.Menu, fg_color="gray20")
        total_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            total_frame,
            text=f"Total Wallet Value: £{total_value:,.2f}",
            font=ctk.CTkFont(family='Consolas', size=14, weight="bold"),
            text_color="gold"
        ).pack(pady=10)