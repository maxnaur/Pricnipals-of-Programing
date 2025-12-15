from m1_create_ctk import _create_top_label, _create_entry_row, _create_button_bottom
from m1_database_interactions import database_connect

def load_NewUserGUI(self):
    """Load Regester GUI"""
    # Create Account Label
    _create_top_label(self.Menu, "Create Account")

    # Username
    self.UserN_En = _create_entry_row(self.Menu, "Username:")
    # Password
    self.Psw_En1 = _create_entry_row(self.Menu, "Password:", show='*')
    # Confirm Password
    self.Psw_En2 = _create_entry_row(self.Menu, "Confirm\nPassword:", show='*')
    # Email
    self.email_EN = _create_entry_row(self.Menu, "Email:")
    # Age
    self.age_En = _create_entry_row(self.Menu, "Age:")
    self.age_En.bind("<Return>", lambda event: Create_account(self)) # press enter to submit on the last item

    # Button
    _create_button_bottom(self.Menu, "Create Account", lambda event: Create_account(self))

def Create_account(self):
    """Connect to database to create the user if enterd things are ok"""
    database = database_connect(self.dbLocation)
    worked = database.Create_account(self)
    database.close()
    if worked:
        self.Load_Menu("Login")