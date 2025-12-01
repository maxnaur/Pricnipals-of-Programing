from CTkMessagebox import CTkMessagebox
import sqlite3 as sql
from cripto_search import fetch_coin_details
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
    
    def check_or_add_crypto(self, coin_id, coin_name=None):
        # coin may not exist in the database but it will after this function
        # Use the existing `Crypto` table (created by e0_database_setup.py).
        self.cur.execute("SELECT ID FROM Crypto WHERE CoinID = ?", (coin_id,))
        row = self.cur.fetchone()
        if row is None:
            # coin does not exist, try to fetch details then add it
            if coin_name is None:
                details = fetch_coin_details(coin_id)
                coin_name = details.get('name', 'Unknown')
            self.cur.execute(
                "INSERT INTO Crypto (Name, CoinID) VALUES (?, ?)",
                (coin_name, coin_id)
            )
            self.db.commit()
            self.cur.execute("SELECT ID FROM Crypto WHERE CoinID = ?", (coin_id,))
            row = self.cur.fetchone()

        if row is None:
            # unexpected: insertion or query failed
            return None

        cryptoID = row[0]
        return cryptoID
    
    def add_crypto_to_wallet(self, userID, coin_id, amount):
        # get crypto ID
        cryptoID = self.check_or_add_crypto(coin_id)

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
        

        


    def close(self):
        self.db.close()