import customtkinter as ctk
import os
from Menu1 import Login_Sidebar
from e0_database_setup import setup_database

class Etternal_GUI:
    def __init__(self):
        super().__init__()

        # Database setup
        self.dbLocation = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Database.db')
        setup_database(self.dbLocation)

        # GUI setup
        ctk.set_appearance_mode("Dark")  # Dark mode only
        ctk.set_default_color_theme("dark-blue")

        self.main = ctk.CTk()
        self.main.title('Crypto Wallet')
        self.main.geometry('500x400')
        

        # Sidebar setup
        Login_Sidebar(self.main, self.dbLocation)

    def closeBase(self):
        self.main.destroy()


if __name__ == "__main__":
    SetupGUI = Etternal_GUI()
    SetupGUI.main.mainloop()