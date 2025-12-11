import customtkinter as ctk
from m2_database_interactions import database_connect

class set_Up_Wallet:
    def __init__(self, Menu, dbLocation, userID):
        self.Menu = Menu
        self.dbLocation = dbLocation
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
        db.cur.execute('''
            SELECT c.Name, c.CoinID, w.Amount 
            FROM Wallet w
            JOIN Crypto c ON w.CryptoID = c.ID
            WHERE w.UserID = ?
        ''', (self.userID,))
        
        holdings = db.cur.fetchall()
        db.close()

        if not holdings:
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

        for coin_name, coin_id, amount in holdings:
            # Fetch current price
            try:
                details = fetch_coin_details(coin_id)
                price_gbp = details.get('market_data', {}).get('current_price', {}).get('gbp', 0)
            except Exception:
                price_gbp = 0

            coin_value = amount * price_gbp
            total_value += coin_value

            # Display individual holding
            holding_frame = ctk.CTkFrame(scrollable_frame, fg_color="gray30")
            holding_frame.pack(fill="x", padx=5, pady=5)

            ctk.CTkLabel(
                holding_frame,
                text=f"{coin_name} ({coin_id.upper()})",
                font=ctk.CTkFont(family='Consolas', size=12, weight="bold")
            ).pack(anchor="w", padx=10, pady=(5, 2))

            ctk.CTkLabel(
                holding_frame,
                text=f"Amount: {amount:.8f}",
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