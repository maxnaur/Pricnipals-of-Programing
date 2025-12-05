import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import requests
import os
from m2_database_interactions import database_connect

from m2_wallet import set_Up_Wallet
from m2_buy import set_Up_Buy
from m2_sell import set_Up_Sell
from m2_transfer import set_Up_Transfer
from m2_qr_code import Display_QR_code


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
            text="Crypto Wallet",
            font=ctk.CTkFont(family='Consolas', size=15)
        )
        self.sidebar.Crypto_Lb.pack(fill="x", pady=5)

        def create_button(text):
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=lambda: self.Load_Menu(text)
            )
            btn.pack(fill="x", pady=5)

        create_button("Wallet")
        create_button("Buy")
        create_button("Sell")
        create_button("Transfer")
        create_button("QR Code\nof userID")

        # Create default frame
        self.Menu = ctk.CTkFrame(self.main, fg_color="gray25")
        self.Menu.pack(fill='both', expand=True)
        self.Load_Menu("Wallet")

    # ------------------------- Menu Switching -------------------------
    def Load_Menu(self, menu_name):
        """Switch between menus."""
        if self.Menu:
            self.Menu.pack_forget()

        self.Menu = ctk.CTkFrame(self.main)
        self.Menu.pack(fill='both', expand=True)

        if menu_name == "Wallet":
            wallet = set_Up_Wallet(self.Menu, self.dbLocation, self.userID)
        elif menu_name == "Buy":
            buy = set_Up_Buy(self.Menu, self.dbLocation, self.userID)
        elif menu_name == "Sell":
            sell = set_Up_Sell(self.Menu, self.dbLocation, self.userID)
        elif menu_name == "Transfer":
            transfer = set_Up_Transfer(self.Menu, self.dbLocation, self.userID)
        elif menu_name == "QR Code\nof userID":
            Display_QR_code(self)


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