from m1_create_ctk import _create_top_label, _create_entry_row, _create_button_bottom
from m1_database_interactions import database_connect
from Menu2 import Wallet_Sidebar

def load_LoginGUI(self, API_search):
    """Load Login GUI"""
    # Login Label
    self.lbl = _create_top_label(self.Menu, "Login")

    # Username
    self.UserN_En = _create_entry_row(self.Menu, "Username:")
    # Password
    self.Psw_En = _create_entry_row(self.Menu, "Password:", show='*')
    self.Psw_En.bind("<Return>", lambda event: Verify_login(self)) # press enter to submit on the last item

    # Login Button
    _create_button_bottom(self.Menu, "Login", lambda: Verify_login(self))

def Verify_login(self):
    """Check login then move onto Menu 2"""
    database = database_connect(self.dbLocation)
    worked = database.Verify_login(self)
    database.close()
    if worked:
        username = self.UserN_En.get().strip()
        self.Menu.pack_forget()
        self.sidebar.pack_forget()
        try:
            wallet = Wallet_Sidebar(self.main, self.dbLocation, self.API_search, username)
        except Exception as exc:
            print(f"Error while loading in: {exc!r}")