import customtkinter as ctk
from m2_database_interactions import database_connect
from CTkMessagebox import CTkMessagebox

class set_Up_Transfer:
    def __init__(self, Menu, dbLocation, API_search, userID):
        self.Menu = Menu
        self.API_search = API_search
        self.dbLocation = dbLocation
        self.userID = userID
        self.Display = ctk.CTkFrame(self.Menu)
        self.Display.pack(fill='both', expand=True)
        # Initialize display
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
                command=lambda cid=crypto_ID, cname=coin_name, cid_str=coin_ID, amt=amount: transfer_prompt(self, cid, cname, amt),
                font=ctk.CTkFont(family='Consolas', size=10),
                height=50
            )
            btn.pack(fill="x", padx=5, pady=5)

        def transfer_prompt(self, crypto_id, coin_name, available_amount):
            """Prompt user for transfer amount."""
            self.Display_resset()
    
            ctk.CTkLabel(
                self.Display,
                text=f"Transfer {coin_name}",
                font=ctk.CTkFont(family='Consolas', size=14, weight="bold")
            ).pack(pady=10)
    
            ctk.CTkLabel(
                self.Display,
                text=f"Available: {available_amount:.2f}",
                font=ctk.CTkFont(family='Consolas', size=11)
            ).pack(pady=5)
    
            # Recipient entry (username or numeric user ID)
            ctk.CTkLabel(
                self.Display,
                text="Recipient (username or user ID):",
                font=ctk.CTkFont(family='Consolas', size=11)
            ).pack(pady=(12, 5))
            self.recipient_entry = ctk.CTkEntry(self.Display, width=250)
            self.recipient_entry.pack(pady=5)
    
            # Amount entry
            ctk.CTkLabel(
                self.Display,
                text="Amount to transfer:",
                font=ctk.CTkFont(family='Consolas', size=11)
            ).pack(pady=(12, 5))
            self.transfer_amount_entry = ctk.CTkEntry(self.Display, width=200)
            self.transfer_amount_entry.pack(pady=5)
    
            def do_transfer():
                recipient = self.recipient_entry.get().strip()
                amt_str = self.transfer_amount_entry.get().strip()
    
                # Basic validation
                try:
                    amount = float(amt_str)
                except Exception:
                    CTkMessagebox(title="Error", message="Enter a valid number for amount", icon="cancel")
                    return
    
                if amount <= 0:
                    CTkMessagebox(title="Error", message="Amount must be positive", icon="cancel")
                    return
                if amount > available_amount:
                    CTkMessagebox(title="Error", message=f"Cannot transfer more than {available_amount:.2f}", icon="cancel")
                    return
                if not recipient:
                    CTkMessagebox(title="Error", message="Enter a recipient username or user ID", icon="cancel")
                    return
    
                # Decide whether recipient is numeric ID or username
                to_userID = None
                to_userName = None
                if recipient.isdigit():
                    to_userID = int(recipient)
                else:
                    to_userName = recipient
    
                db = database_connect(self.dbLocation)
                try:
                    success, msg = db.transfer_crypto_to_account(self.userID, to_userID, to_userName, crypto_id, amount)
                    if success:
                        db.Tansaction_UserToUser(crypto_id, self.userID, to_userID, to_userName, amount)
                    db.close()
                except Exception as e:
                    db.close()
                    CTkMessagebox(title="Error", message=f"Database error: {e}", icon="cancel")
                    return
    
                if success:
                    # refresh display
                    self.Display_resset()
                    self.display_wallet()
                    CTkMessagebox(title="Success", message=msg or "Transfer successful", icon="check")
                else:
                    CTkMessagebox(title="Error", message=msg or "Transfer failed", icon="cancel")
    
            btn = ctk.CTkButton(
                self.Display,
                text="Confirm Transfer",
                font=('Consolas', 12),
                width=160,
                height=40,
                command=do_transfer
            )
            btn.pack(pady=16)

    def Display_resset(self):
        """clear screen"""
        self.Display.pack_forget()
        self.Display = ctk.CTkFrame(self.Menu)
        self.Display.pack(fill='both', expand=True)