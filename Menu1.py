import customtkinter as ctk
from m1_login import load_LoginGUI
from m1_register import load_NewUserGUI

class Login_Sidebar:
    """Create first Sidebar which will allow the user to login and create an account"""
    def __init__(self, main, dbLocation, API_search):
        """Initialize the login sidebar."""
        self.main = main
        self.dbLocation = dbLocation
        self.API_search = API_search
        self.sidebar = ctk.CTkFrame(self.main, width=120, fg_color="gray30")
        self.sidebar.pack(side='left', fill='y')
        self.Menu = None
        self.Setup_sidebar()

    # ------------------------- Sidebar Setup -------------------------
    def Setup_sidebar(self):
        """Set up sidebar buttons and layout."""
        self.sidebar.Crypto_Lb = ctk.CTkLabel(
            self.sidebar,
            text="Crypto Login",
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

        create_button("Login")
        create_button("Register")

        # Create default frame
        self.Menu = ctk.CTkFrame(self.main, fg_color="gray25")
        self.Menu.pack(fill='both', expand=True)
        self.Load_Menu("Login")

    # ------------------------- Menu Switching -------------------------
    def Load_Menu(self, menu_name):
        """Switch between Login, and Register menus."""
        if self.Menu:
            self.Menu.pack_forget()

        self.Menu = ctk.CTkFrame(self.main)
        self.Menu.pack(fill='both', expand=True)

        if menu_name == "Login":
            load_LoginGUI(self, self.API_search)
        elif menu_name == "Register":
            load_NewUserGUI(self)