import customtkinter as ctk
from m2_database_interactions import database_connect
#from crypto_API import fetch_coin_details
from CTkMessagebox import CTkMessagebox

class set_Up_Transfer:
    def __init__(self, Menu, dbLocation, userID):
        self.Menu = Menu
        self.dbLocation = dbLocation
        self.userID = userID
        self.display_transfer()

    def display_transfer(self):
        """Display transfer interface."""
        ctk.CTkLabel(
            self.Menu,
            text="Transfer Cryptocurrency",
            font=ctk.CTkFont(family='Consolas', size=15)
        ).pack(pady=14)

        # Recipient ID input
        recipient_frame = ctk.CTkFrame(self.Menu)
        recipient_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            recipient_frame,
            text="Recipient User ID:",
            font=ctk.CTkFont(family='Consolas', size=11)
        ).pack(side="left", padx=(0, 10))

        recipient_entry = ctk.CTkEntry(recipient_frame, width=150)
        recipient_entry.pack(side="left")

        # Crypto selection
        db = database_connect(self.dbLocation)
        holdings = db.get_user_holdings(self.userID)
        db.close()

        if not holdings:
            ctk.CTkLabel(
                self.Menu,
                text="No cryptocurrencies in your wallet to transfer",
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
                command=lambda cid=crypto_id, cname=coin_name, cid_str=coin_id_str, amt=amount, rid=recipient_entry: self.transfer_prompt(rid, cid, cname, cid_str, amt, price_gbp),
                font=ctk.CTkFont(family='Consolas', size=10),
                height=50
            )
            btn.pack(fill="x", padx=5, pady=5)

    def transfer_prompt(self, recipient_entry, crypto_id, coin_name, coin_id_str, available_amount, price_gbp):
        """Prompt user for transfer amount."""
        recipient_id_str = recipient_entry.get().strip()

        if not recipient_id_str:
            CTkMessagebox(title="Error", message="Please enter a recipient User ID", icon="cancel")
            return

        try:
            recipient_id = int(recipient_id_str)
        except ValueError:
            CTkMessagebox(title="Error", message="Recipient User ID must be a number", icon="cancel")
            return

        if recipient_id == self.userID:
            CTkMessagebox(title="Error", message="Cannot transfer to yourself", icon="cancel")
            return

        # Create a new window for transfer
        transfer_window = ctk.CTkToplevel(self.Menu)
        transfer_window.title(f"Transfer {coin_name}")
        transfer_window.geometry("500x300")

        ctk.CTkLabel(
            transfer_window,
            text=f"Transfer {coin_name}",
            font=ctk.CTkFont(family='Consolas', size=14, weight="bold")
        ).pack(pady=10)

        ctk.CTkLabel(
            transfer_window,
            text=f"To User ID: {recipient_id}",
            font=ctk.CTkFont(family='Consolas', size=11)
        ).pack(pady=5)

        ctk.CTkLabel(
            transfer_window,
            text=f"Available: {available_amount:.8f}",
            font=ctk.CTkFont(family='Consolas', size=11)
        ).pack(pady=5)

        ctk.CTkLabel(
            transfer_window,
            text=f"Current price: £{price_gbp:,.2f}",
            font=ctk.CTkFont(family='Consolas', size=11)
        ).pack(pady=5)

        # Amount entry
        ctk.CTkLabel(
            transfer_window,
            text="Amount to transfer:",
            font=ctk.CTkFont(family='Consolas', size=11)
        ).pack(pady=(15, 5))

        amount_entry = ctk.CTkEntry(transfer_window, width=200)
        amount_entry.pack(pady=5)

        def execute_transfer():
            try:
                transfer_amount = float(amount_entry.get().strip())
            except ValueError:
                CTkMessagebox(title="Error", message="Enter a valid number", icon="cancel")
                return

            # Validate amount
            if transfer_amount <= 0:
                CTkMessagebox(title="Error", message="Amount must be positive", icon="cancel")
                return

            if transfer_amount > available_amount:
                CTkMessagebox(
                    title="Error", 
                    message=f"Cannot transfer more than {available_amount:.8f} {coin_name}", 
                    icon="cancel"
                )
                return

            # Perform transfer
            db = database_connect(self.dbLocation)
            try:
                success, message = db.transfer_crypto_to_account(self.userID, recipient_id, crypto_id, transfer_amount)
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
                total_gbp = transfer_amount * price_gbp
                CTkMessagebox(
                    title="Success",
                    message=f"Transferred {transfer_amount:.8f} {coin_name} to User ID {recipient_id} (Value: £{total_gbp:,.2f})",
                    icon="check"
                )
                transfer_window.destroy()
                # Refresh display
                self.Menu.pack_forget()
                self.Menu = ctk.CTkFrame(self.Menu.master)
                self.Menu.pack(fill='both', expand=True)
                self.display_transfer()
            else:
                CTkMessagebox(
                    title="Error",
                    message=message,
                    icon="cancel"
                )

        ctk.CTkButton(
            transfer_window,
            text="Confirm Transfer",
            command=execute_transfer,
            width=150,
            height=40
        ).pack(pady=20)