import customtkinter as ctk
import qrcode
import os
from m2_database_interactions import database_connect

from m2_wallet import set_Up_Wallet
from m2_buy import set_Up_Buy
from m2_sell import set_Up_Sell
from m2_transfer import set_Up_Transfer
from m2_qr_code import Display_QR_code


class Wallet_Sidebar:
    def __init__(self, main, dbLocation, API_search, username):
        """Initialize the wallet sidebar."""
        self.main = main
        self.main.geometry('1000x800')
        self.sidebar = ctk.CTkFrame(self.main, width=120, fg_color="gray30")
        self.sidebar.pack(side='left', fill='y')
        self.dbLocation = dbLocation
        self.API_search = API_search
        self.Menu = None

        # Database connection
        self.db = database_connect(self.dbLocation)
        self.userID = self.db.get_userID(username)
        self.holdings = self.db.get_userWallet(self.userID)
        self.db.close()
        
        # make QR code and save to file
        qr_image = qrcode.make(self.userID)
        qrLocation = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_wallet_qr.png')
        qr_image.save(qrLocation)

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
            wallet = set_Up_Wallet(self.Menu, self.dbLocation, self.API_search, self.userID)
        elif menu_name == "Buy":
            buy = set_Up_Buy(self.Menu, self.dbLocation, self.API_search, self.userID)
        elif menu_name == "Sell":
            sell = set_Up_Sell(self.Menu, self.dbLocation, self.API_search, self.userID)
        elif menu_name == "Transfer":
            transfer = set_Up_Transfer(self.Menu, self.dbLocation, self.API_search, self.userID)
        elif menu_name == "QR Code\nof userID":
            Display_QR_code(self)
            self.Load_Menu("Wallet")
