import customtkinter as ctk
import os
from crypto_API import API_search
from setup_database import setup_database
from Menu1 import Authentication_Sidebar

class Etternal_GUI:
    """Create innishal Window that most things will resside in"""
    def __init__(self):
        super().__init__()

        # API setup
        self.API_search = API_search()

        # Database setup
        self.dbLocation = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Database.db')
        setup_database(self.dbLocation, self.API_search)

        # GUI setup
        ctk.set_appearance_mode("Dark")  # Dark mode only
        ctk.set_default_color_theme("dark-blue")

        self.main = ctk.CTk()
        self.main.title('Crypto Wallet')
        self.main.geometry('500x400')

        # Sidebar setup
        Authentication_Sidebar(self.main, self.dbLocation, self.API_search)


if __name__ == "__main__":
    SetupGUI = Etternal_GUI()
    SetupGUI.main.mainloop()