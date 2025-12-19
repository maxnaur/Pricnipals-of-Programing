import customtkinter as ctk
from m2_database_interactions import database_connect
from CTkMessagebox import CTkMessagebox

class set_Up_Sell:
    """Allow a user to sell the owned crypto"""
    def __init__(self, Menu, dbLocation, API_search, userID):
        self.Menu = Menu
        self.dbLocation = dbLocation
        self.API_search = API_search
        self.userID = userID
        self.Display = None
        # Initialize display
        self.Display_resset(True)
    
    def Display_resset(self, first_time=False):
        """Resset everything to start"""
        if not first_time:
            self.Display.pack_forget()
        self.Display = ctk.CTkFrame(self.Menu)
        self.Display.pack(fill='both', expand=True)
        # display wallet
        self.display_wallet()

    def display_wallet(self):
        """Display all cryptocurrencies owned by the user for selling."""
        # Create header
        ctk.CTkLabel(
            self.Display,
            text="Sell Cryptocurrency",
            font=ctk.CTkFont(family='Consolas', size=15)
        ).pack(pady=14)

        # Fetch wallet data
        db = database_connect(self.dbLocation)
        holdings = db.get_user_holdings(self.userID)
        db.close()

        if not holdings:
            ctk.CTkLabel(
                self.Display,
                text="No cryptocurrencies in your wallet to sell",
                font=ctk.CTkFont(family='Consolas', size=12)
            ).pack(pady=10)
            return

        # Create scrollable frame for holdings
        container = ctk.CTkFrame(self.Display)
        container.pack(padx=10, pady=10, fill="both", expand=True)
        
        scrollable_frame = ctk.CTkScrollableFrame(container)
        scrollable_frame.pack(fill="both", expand=True)
        
        Coin_IDs = []
        for _, _, coin_ID, amount in holdings:
            Coin_IDs.append(coin_ID)
        coins_details = self.API_search.fetch_crypto_batch(Coin_IDs)

        for crypto_ID, coin_name, coin_ID, amount in holdings:
            # Fetch current price
            try:
                details = coins_details[coin_ID]
                price_gbp = details.get('current_price', {})
            except Exception:
                price_gbp = 0

            coin_value = amount * price_gbp

            # Display individual holding as a button
            holding_frame = ctk.CTkFrame(scrollable_frame, fg_color="gray30")
            holding_frame.pack(fill="x", padx=5, pady=5)

            # Create clickable button
            btn = ctk.CTkButton(
                holding_frame,
                text=f"{coin_name} ({coin_ID.upper()})  |  Amount: {amount:.2f}  |  Price: £{price_gbp:,.2f}  |  Value: £{coin_value:,.2f}",
                fg_color="gray30",
                hover_color="#494545",
                text_color="white",
                command=lambda cid=crypto_ID, cname=coin_name, cid_str=coin_ID, amt=amount: self.sell_prompt(cid, cname, cid_str, amt, price_gbp),
                font=ctk.CTkFont(family='Consolas', size=10),
                height=50
            )
            btn.pack(fill="x", padx=5, pady=5)

    def sell_prompt(self, crypto_id, coin_name, coin_ID, available_amount, price_gbp):
        """Prompt user for sell amount."""
        # Create a new window for selling
        self.sell_window = ctk.CTkToplevel(self.Display)
        self.sell_window.title(f"Sell {coin_name}")
        self.sell_window.geometry("400x300")

        ctk.CTkLabel(
            self.sell_window,
            text=f"Sell {coin_name}",
            font=ctk.CTkFont(family='Consolas', size=14, weight="bold")
        ).pack(pady=10)

        ctk.CTkLabel(
            self.sell_window,
            text=f"Available: {available_amount:.2f}",
            font=ctk.CTkFont(family='Consolas', size=11)
        ).pack(pady=5)

        ctk.CTkLabel(
            self.sell_window,
            text=f"Current price: £{price_gbp:,.2f}",
            font=ctk.CTkFont(family='Consolas', size=11)
        ).pack(pady=5)

        # Amount entry
        ctk.CTkLabel(
            self.sell_window,
            text="Amount to sell:",
            font=ctk.CTkFont(family='Consolas', size=11)
        ).pack(pady=(15, 5))

        self.amount_entry = ctk.CTkEntry(self.sell_window, width=200)
        self.amount_entry.pack(pady=5)

        btn = ctk.CTkButton(
            self.sell_window,
            text="Confirm Sell",
            font=('Consolas', 12),
            width=150,
            height=40
        )
        coin = (crypto_id, coin_name, available_amount, price_gbp)
        # Attach coin data to the button widget
        btn.coin = coin
        # Capture the coin value for the command callback
        btn.configure(command=lambda c=coin: self.execute_sell(c))
        btn.pack(pady=20)


    def execute_sell(self, coin):
        """sell the things and interact with database"""
        (crypto_id, coin_name, available_amount, price_gbp) = coin
        try:
            sell_amount = float(self.amount_entry.get().strip())
        except ValueError:
            CTkMessagebox(title="Error", message="Enter a valid number", icon="cancel")
            return

        # Validate amount
        if sell_amount <= 0:
            CTkMessagebox(title="Error", message="Amount must be positive", icon="cancel")
            return

        if sell_amount > available_amount:
            CTkMessagebox(
                title="Error", 
                message=f"Cannot sell more than {available_amount:.2f} {coin_name}", 
                icon="cancel"
            )
            return

        # Perform sell
        db = database_connect(self.dbLocation)
        try:
            success = db.remove_crypto_from_wallet(self.userID, crypto_id, sell_amount)
            if success:
                db.Tansaction_Sell(crypto_id, self.userID, sell_amount)
            db.close()
        except Exception as e:
            db.close()
            CTkMessagebox(
                title="Error",
                message=f"Database error: {str(e)}",
                icon="cancel"
            )
            return

        if success:
            total_gbp = sell_amount * price_gbp
            # Refresh wallet display
            self.sell_window.destroy()
            self.Display_resset()
            
            CTkMessagebox(
                title="Success",
                message=f"Sold {sell_amount:.2f} {coin_name} for £{total_gbp:,.2f}",
                icon="check"
            )
        else:
            CTkMessagebox(
                title="Error",
                message="Failed to sell cryptocurrency. Check that you have sufficient balance.",
                icon="cancel"
            )
    