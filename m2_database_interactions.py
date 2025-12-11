from CTkMessagebox import CTkMessagebox
import sqlite3 as sql
<<<<<<< Updated upstream
from cripto_search import fetch_coin_details
=======
from datetime import datetime, timezone
>>>>>>> Stashed changes
import re
import bcrypt

class database_connect():
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
        self.cur.execute("SELECT CryptoID, Amount FROM Wallet WHERE UserID = ?", (userID,))
        userWallet = self.cur.fetchone()
        return userWallet
    
    def check_or_add_crypto(self, crypto_API, coinID, coin_Name=None):
        # coin may not exist in the database but it will after this function
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
                "SELECT Amount FROM Wallet WHERE UserID = ? AND CryptoID = ?",
                (userID, cryptoID)
            )
            result = self.cur.fetchone()

            if result is None:
                return False

            current_amount = result[0]

            # Validate amount (with small tolerance for floating point comparison)
            if amount > current_amount + 1e-8:
                return False

            # If selling all (or nearly all due to float precision), delete the wallet entry
            if abs(amount - current_amount) < 1e-8:
                self.cur.execute(
                    "DELETE FROM Wallet WHERE UserID = ? AND CryptoID = ?",
                    (userID, cryptoID)
                )
            else:
                # Update with new amount
                new_amount = current_amount - amount
                self.cur.execute(
                    "UPDATE Wallet SET Amount = ? WHERE UserID = ? AND CryptoID = ?",
                    (new_amount, userID, cryptoID)
                )

            self.db.commit()
            return True
        except Exception:
            return False
        

    def transfer_crypto(self, from_userID, to_userID, cryptoID, amount):
        """Transfer cryptocurrency from one user to another."""
        try:
            # Validate recipient exists
            self.cur.execute("SELECT ID FROM User WHERE ID = ?", (to_userID,))
            if self.cur.fetchone() is None:
                return False, "Recipient user not found"

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
        
    # ----------------------------- Transactions Log interactions -----------------------------
    def Transaction_Buy(self, cryptoID, userID, amount):
        self.cur.execute(
            "INSERT INTO Transactions_Buy (CryptoID, UserID, Amount, DateTime) VALUES (?, ?, ?, ?)",
            (cryptoID, userID, amount, datetime.now(timezone.utc))
        )
    
    def Tansaction_Sell(self, cryptoID, userID, amount):
        self.cur.execute(
            "INSERT INTO Transactions_Buy (CryptoID, UserID, Amount, DateTime) VALUES (?, ?, ?, ?)",
            (cryptoID, userID, amount, datetime.now(timezone.utc))
        )

    def Tansaction_UserToUser(self, cryptoID, from_userID, to_userID, amount):
        self.cur.execute(
            "INSERT INTO Transactions_Buy (CryptoID, UserFromID, UserToID, Amount, DateTime) VALUES (?, ?, ?, ?)",
            (cryptoID, from_userID, to_userID, amount, datetime.now(timezone.utc))
        )

    def close(self):
        self.db.close()