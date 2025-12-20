from CTkMessagebox import CTkMessagebox
import sqlite3 as sql
from datetime import datetime, timezone
import re
import bcrypt

class database_connect():
    """Connect to database to allow for all changes in Menu 2"""
    def __init__(self, dbLocation):
        self.dbLocation = dbLocation
        self.db = sql.connect(self.dbLocation)
        self.cur = self.db.cursor()

    def get_userID(self, username):
        """Fetch user ID from username"""
        self.cur.execute("SELECT ID FROM User WHERE Username = ?", (username,))
        row = self.cur.fetchone()
        return row[0] if row else None
    
    def get_userWallet(self, userID):
        """Fetch the user's wallet from the database."""
        self.cur.execute("""SELECT c.CoinID, c.Name, w.Amount 
                        FROM Wallet w JOIN Crypto c ON w.CryptoID = c.ID 
                        WHERE w.UserID = ?""", (userID,))
        userWallet = self.cur.fetchall()  # Use fetchall() to get all rows

        # make sure its a 2 dimentional list
        if userWallet != None:
            if not isinstance(userWallet, list):
                userWallet = [userWallet] # get the first item from a 1 dimentional list
        return userWallet
    
    def check_or_add_crypto(self, crypto_API, coinID, coin_Name=None):
        """coin may not exist in the database but it will after this function"""
        # Use the existing `Crypto` table (created by e0_database_setup.py).
        self.cur.execute("SELECT ID FROM Crypto WHERE CoinID = ?", (coinID,))
        row = self.cur.fetchone()
        if row is None:
            # coin does not exist, try to fetch details then add it
            if coin_Name is None:
                details = crypto_API.fetch_single_coin_details(coinID)
                coin_Name = details.get('name', 'Unknown')
            self.cur.execute(
                "INSERT INTO Crypto (Name, CoinID) VALUES (?, ?)",
                (coin_Name, coinID)
            )
            self.db.commit()
            self.cur.execute("SELECT ID FROM Crypto WHERE CoinID = ?", (coinID,))
            row = None
            row = self.cur.fetchone()

        if row is None:
            # unexpected: insertion or query failed
            return None

        cryptoID = row[0]
        return cryptoID
    
    def add_crypto_to_wallet(self, crypto_API, userID, coinID, coin_Name, amount):
        """Add Cryto currency to A user account"""
        # get crypto ID
        cryptoID = self.check_or_add_crypto(crypto_API, coinID, coin_Name)

        # check if user already has this crypto in their wallet
        self.cur.execute("SELECT Amount FROM Wallet WHERE UserID = ? AND CryptoID = ?", (userID, cryptoID))
        result = self.cur.fetchone()
        if result is not None:
            # update existing amount
            new_amount = result[0] + amount
            self.cur.execute(
                "UPDATE Wallet SET Amount = ? WHERE UserID = ? AND CryptoID = ?",
                (new_amount, userID, cryptoID)
            )
        else:
            # insert new record
            self.cur.execute(
                "INSERT INTO Wallet (UserID, CryptoID, Amount) VALUES (?, ?, ?)",
                (userID, cryptoID, amount)
            )
        self.db.commit()
        

    def get_user_holdings(self, userID):
        """Fetch all cryptocurrencies and amounts owned by a user."""
        try:
            self.cur.execute('''
                SELECT c.ID, c.Name, c.CoinID, w.Amount 
                FROM Wallet w
                JOIN Crypto c ON w.CryptoID = c.ID
                WHERE w.UserID = ?
            ''', (userID,))
            return self.cur.fetchall()
        except Exception:
            return []

    def remove_crypto_from_wallet(self, userID, cryptoID, amount):
        """Remove cryptocurrency from user's wallet."""
        try:
            # Check current amount
            self.cur.execute(
                "SELECT ID, Amount FROM Wallet WHERE UserID = ? AND CryptoID = ?",
                (userID, cryptoID)
            )
            result = self.cur.fetchone()

            if result is None:
                return False

            ID = result[0]
            Totale_amount = result[1]

            # Validate amount (with small tolerance for floating point comparison)
            if amount > Totale_amount:
                return False

            # If selling all (or nearly all due to float precision), delete the wallet entry
            if abs(amount - Totale_amount) < 1e-2:
                self.cur.execute(
                    "DELETE FROM Wallet WHERE ID = ?",
                    (ID,)
                )
            else:
                # Update with new amount
                new_amount = Totale_amount - amount
                self.cur.execute(
                    "UPDATE Wallet SET Amount = ? WHERE ID = ?",
                    (new_amount, ID)
                )

            self.db.commit()
            return True
        except Exception as e:
            print(f"Database error in remove_crypto_from_wallet: {e}")
            return False
        

    def transfer_crypto_to_account(self, from_userID, to_userID, to_userName, cryptoID, amount):
        """Transfer cryptocurrency from one user to another."""
        # Validate inputs
        if to_userID is None and to_userName is None:
            return False, "Recipient information is required"

        # prevent sql injection
        if to_userName is not None:
            if not re.match(r'^[a-zA-Z]+$', to_userName):
                return False, "Invalid recipient username"
        
        try:
            is_valid, temp_userID = self.check_userID(to_userID, to_userName)
            if not is_valid:
                return False, "Recipient user not found"
            to_userID = temp_userID
            
            if from_userID == to_userID:
                return False, "Cannot transfer to the same account"

            # Check sender has sufficient balance
            self.cur.execute(
                "SELECT Amount FROM Wallet WHERE UserID = ? AND CryptoID = ?",
                (from_userID, cryptoID)
            )
            result = self.cur.fetchone()

            if result is None or result[0] < amount:
                return False, "Insufficient balance"

            # Deduct from sender
            new_sender_amount = result[0] - amount
            if abs(new_sender_amount) < 1e-8:  # Selling all
                self.cur.execute(
                    "DELETE FROM Wallet WHERE UserID = ? AND CryptoID = ?",
                    (from_userID, cryptoID)
                )
            else:
                self.cur.execute(
                    "UPDATE Wallet SET Amount = ? WHERE UserID = ? AND CryptoID = ?",
                    (new_sender_amount, from_userID, cryptoID)
                )

            # Add to recipient
            self.cur.execute(
                "SELECT Amount FROM Wallet WHERE UserID = ? AND CryptoID = ?",
                (to_userID, cryptoID)
            )
            recipient_result = self.cur.fetchone()

            if recipient_result is not None:
                new_recipient_amount = recipient_result[0] + amount
                self.cur.execute(
                    "UPDATE Wallet SET Amount = ? WHERE UserID = ? AND CryptoID = ?",
                    (new_recipient_amount, to_userID, cryptoID)
                )
            else:
                self.cur.execute(
                    "INSERT INTO Wallet (UserID, CryptoID, Amount) VALUES (?, ?, ?)",
                    (to_userID, cryptoID, amount)
                )

            self.db.commit()
            return True, "Transfer successful"
        except Exception as e:
            return False, f"Transfer failed: {str(e)}"
        
    def check_userID (self, userID, username):
        # prioritize username if provided
        if username is None:
            # Validate recipient exists
            self.cur.execute("SELECT ID FROM User WHERE ID = ?", (userID,))
            if self.cur.fetchone() is None:
                return False, None
        else:
            # Fetch recipient userID from username
            self.cur.execute("SELECT ID FROM User WHERE Username = ?", (username,))
            result = self.cur.fetchone()
            if result is None:
                return False, None
            userID = result[0]
        return True, userID
        
    # ----------------------------- Transactions Log interactions -----------------------------
    def Transaction_Buy(self, cryptoID, userID, amount):
        """Log Buy with time"""
        self.cur.execute(
            "INSERT INTO Transactions_Buy (CryptoID, UserID, Amount, DateTime) VALUES (?, ?, ?, ?)",
            (cryptoID, userID, amount, datetime.now(timezone.utc).isoformat())
        )
        self.db.commit()
    
    def Tansaction_Sell(self, cryptoID, userID, amount):
        """Log Sell with time"""
        self.cur.execute(
            "INSERT INTO Transactions_Sell (CryptoID, UserID, Amount, DateTime) VALUES (?, ?, ?, ?)",
            (cryptoID, userID, amount, datetime.now(timezone.utc).isoformat())
        )
        self.db.commit()

    def Tansaction_UserToUser(self, cryptoID, from_userID, to_userID, to_userName, amount):
        """Log Transfer with time"""
        # no need to check if valid because it will be if you got to this point
        _, temp_userID = self.check_userID(to_userID, to_userName)
        self.cur.execute(
            "INSERT INTO Transactions_UserToUser (CryptoID, UserFromID, UserToID, Amount, DateTime) VALUES (?, ?, ?, ?, ?)",
            (cryptoID, from_userID, temp_userID, amount, datetime.now(timezone.utc).isoformat())
        )
        self.db.commit()

    def close(self):
        self.db.close()