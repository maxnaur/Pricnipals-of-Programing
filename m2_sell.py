import customtkinter as ctk
from m2_database_interactions import database_connect
#from crypto_API import fetch_coin_details
from CTkMessagebox import CTkMessagebox

class set_Up_Sell:
    def __init__(self, Menu, dbLocation, userID):
        self.Menu = Menu
        self.dbLocation = dbLocation
        self.userID = userID
        self.display_wallet()

    def display_wallet(self):
        """Display all cryptocurrencies owned by the user for selling."""
        # Create header
        ctk.CTkLabel(
            self.Menu,
            text="Sell Cryptocurrency",
            font=ctk.CTkFont(family='Consolas', size=15)
        ).pack(pady=14)

        # Fetch wallet data
        db = database_connect(self.dbLocation)
        holdings = db.get_user_holdings(self.userID)
        db.close()

        if not holdings:
            ctk.CTkLabel(
                self.Menu,
                text="No cryptocurrencies in your wallet to sell",
                font=ctk.CTkFont(family='Consolas', size=12)
            ).pack(pady=10)
            return

        # Create scrollable frame for holdings
        container = ctk.CTkFrame(self.Menu)
        container.pack(padx=10, pady=10, fill="both", expand=True)
        
        scrollable_frame = ctk.CTkScrollableFrame(container)
        scrollable_frame.pack(fill="both", expand=True)

        for crypto_id, coin_name, coin_id_str, amount in holdings:
            # Fetch current price
            try:
                details = fetch_coin_details(coin_id_str)
                price_gbp = details.get('market_data', {}).get('current_price', {}).get('gbp', 0)
            except Exception:
                price_gbp = 0

            coin_value = amount * price_gbp

            # Display individual holding as a button
            holding_frame = ctk.CTkFrame(scrollable_frame, fg_color="gray30")
            holding_frame.pack(fill="x", padx=5, pady=5)

            # Create clickable button
            btn = ctk.CTkButton(
                holding_frame,
                text=f"{coin_name} ({coin_id_str.upper()})  |  Amount: {amount:.8f}  |  Price: £{price_gbp:,.2f}  |  Value: £{coin_value:,.2f}",
                fg_color="gray30",
                hover_color="#494545",
                text_color="white",
                command=lambda cid=crypto_id, cname=coin_name, cid_str=coin_id_str, amt=amount: self.sell_prompt(cid, cname, cid_str, amt, price_gbp),
                font=ctk.CTkFont(family='Consolas', size=10),
                height=50
            )
            btn.pack(fill="x", padx=5, pady=5)

    def sell_prompt(self, crypto_id, coin_name, coin_id_str, available_amount, price_gbp):
        """Prompt user for sell amount."""
        # Create a new window for selling
        sell_window = ctk.CTkToplevel(self.Menu)
        sell_window.title(f"Sell {coin_name}")
        sell_window.geometry("400x300")

        ctk.CTkLabel(
            sell_window,
            text=f"Sell {coin_name}",
            font=ctk.CTkFont(family='Consolas', size=14, weight="bold")
        ).pack(pady=10)

        ctk.CTkLabel(
            sell_window,
            text=f"Available: {available_amount:.8f}",
            font=ctk.CTkFont(family='Consolas', size=11)
        ).pack(pady=5)

        ctk.CTkLabel(
            sell_window,
            text=f"Current price: £{price_gbp:,.2f}",
            font=ctk.CTkFont(family='Consolas', size=11)
        ).pack(pady=5)

        # Amount entry
        ctk.CTkLabel(
            sell_window,
            text="Amount to sell:",
            font=ctk.CTkFont(family='Consolas', size=11)
        ).pack(pady=(15, 5))

        amount_entry = ctk.CTkEntry(sell_window, width=200)
        amount_entry.pack(pady=5)

        def execute_sell():
            try:
                sell_amount = float(amount_entry.get().strip())
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
                    message=f"Cannot sell more than {available_amount:.8f} {coin_name}", 
                    icon="cancel"
                )
                return

            # Perform sell
            db = database_connect(self.dbLocation)
            try:
                success = db.remove_crypto_from_wallet(self.userID, crypto_id, sell_amount)
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
                CTkMessagebox(
                    title="Success",
                    message=f"Sold {sell_amount:.8f} {coin_name} for £{total_gbp:,.2f}",
                    icon="check"
                )
                sell_window.destroy()
                # Refresh wallet display
                self.Menu.pack_forget()
                self.Menu = ctk.CTkFrame(self.Menu.master)
                self.Menu.pack(fill='both', expand=True)
                self.display_wallet()
            else:
                CTkMessagebox(
                    title="Error",
                    message="Failed to sell cryptocurrency. Check that you have sufficient balance.",
                    icon="cancel"
                )

        ctk.CTkButton(
            sell_window,
            text="Confirm Sell",
            command=execute_sell,
            width=150,
            height=40
        ).pack(pady=20)