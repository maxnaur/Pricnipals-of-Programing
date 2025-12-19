from CTkMessagebox import CTkMessagebox
import sqlite3 as sql
import re
import bcrypt

from setup_database import Add_Coins, Add_Wallet

class database_connect():
    """Connect to database to allow for all changes in Menu 1 with error checking"""
    def __init__(self, API_Search, dbLocation):
        self.API_Search = API_Search
        self.dbLocation = dbLocation
        self.db = sql.connect(self.dbLocation)
        self.cur = self.db.cursor()
    
    # -------------------------- Login Section --------------------------
    def Verify_login(self, higher_self):
        """Verify user credentials."""
        username = higher_self.UserN_En.get().strip()
        password = higher_self.Psw_En.get().strip()

        if not username or not password:
            CTkMessagebox(title="Error", message="Both fields must be filled", icon="cancel")
            return False

        self.cur.execute("SELECT Password FROM User WHERE Username = ?", (username,))
        foundPassword = self.cur.fetchone()

        if foundPassword is None:
            CTkMessagebox(title="Error", message="User not found", icon="cancel")
            return False
        else:
            stored_hash = foundPassword[0]
            passwordCheck = password.encode('utf-8')
            if not bcrypt.checkpw(passwordCheck, stored_hash):
                CTkMessagebox(title="Error", message="Incorrect password", icon="cancel")
                return False
            else:
                CTkMessagebox(title="Success", message=f"Welcome back, {username}!", icon="check")
                return True

    # -------------------------- Create Account Section --------------------------
    def Create_account(self, higher_self):
        """Create a new user account with full validation."""
        username = higher_self.UserN_En.get().strip()
        email = higher_self.email_EN.get().strip()
        password = higher_self.Psw_En1.get()
        confirm = higher_self.Psw_En2.get()
        age = higher_self.age_En.get().strip()

        # Validate inputs
        if not all([username, email, password, confirm, age]):
            CTkMessagebox(title="Error", message="Not all items are filled", icon="cancel")
            return False

        # Age validation
        if not age.isdigit():
            CTkMessagebox(title="Error", message="Age must be a number", icon="cancel")
            return False
        if int(age) < 18:
            CTkMessagebox(title="Error", message="You must be over 18 to create an account", icon="cancel")
            return False

        # Email validation
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            CTkMessagebox(title="Error", message="Invalid email format", icon="cancel")
            return False

        # Password validation
        if password != confirm:
            CTkMessagebox(title="Error", message="Passwords do not match", icon="cancel")
            return False
        if len(password) < 8:
            CTkMessagebox(title="Error", message="Password must be at least 8 characters long", icon="cancel")
            return False
        if password.lower() == password or password.upper() == password:
            CTkMessagebox(title="Error", message="Password must include both upper and lower case letters", icon="cancel")
            return False
        if not re.search(r"\d", password):
            CTkMessagebox(title="Error", message="Password must contain at least one number", icon="cancel")
            return False
        if not re.search(r"[^a-zA-Z0-9]", password):
            CTkMessagebox(title="Error", message="Password must contain at least one special character", icon="cancel")
            return False

        # Username validation
        if not re.match(r"^[a-zA-Z0-9 ]+$", username):
            CTkMessagebox(title="Error", message="Username can only contain letters, numbers, and spaces", icon="cancel")
            return False

        self.cur.execute("SELECT COUNT(*) FROM User WHERE Username = ?", (username,))
        if self.cur.fetchone()[0] != 0:
            CTkMessagebox(title="Error", message="Username already exists", icon="cancel")
            return False

        hashedPassword = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        self.cur.execute('''
            INSERT INTO User (Username, Email, Password, AccessLevel) 
            VALUES (?, ?, ?, ?)''',
            (username, email, hashedPassword, 0)
        )

        # Set up initial wallet for user with dummy data
        WALLET = {
            'bitcoin': 0.5,
            'ethereum': 2,
            'tether': 1000,
            'binancecoin': 1,
            'solana': 10,
            'ripple': 500,
        }

        self.cur.execute("SELECT ID FROM User WHERE Username = ?", (username,))
        User_ID = self.cur.fetchone()[0]

        crypto_ID_List = Add_Coins(self.cur, WALLET, self.API_Search)
        Add_Wallet(self.cur, User_ID, crypto_ID_List, WALLET)
        
        self.db.commit()

        CTkMessagebox(title="Success", message="Account created successfully!", icon="check")
    
    
    def close(self):
        self.db.close()