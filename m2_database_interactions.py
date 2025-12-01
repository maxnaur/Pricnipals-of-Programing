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
        user_id = self.cur.fetchone()[0]
        return user_id
    
    def get_userWallet(self, userID):
        """Fetch the user's wallet from the database."""
        self.cur.execute("SELECT CryptoID, Amount FROM Wallet WHERE UserID = ?", (userID,))
        userWallet = self.cur.fetchone()
        return userWallet
    
    def check_or_add_crypto(self, coin_id, coin_name=None):
        # coin may not exist in the database but it will after this function
        self.cur.execute("SELECT ID FROM Cryptocurrency WHERE CoinID = ?", (coin_id,))
        result = self.cur.fetchone()
        if result is not None:
            if coin_name is None:
                details = fetch_coin_details(coin_id)
                coin_name = details.get('name', 'Unknown')
            # coin does not exist, add it
            self.cur.execute(
                "INSERT INTO Cryptocurrency (CoinID, Name) VALUES (?, ?)",
                (coin_id, coin_name)
            )
            self.db.commit()
        criptoID = self.cur.execute("SELECT ID FROM Cryptocurrency WHERE CoinID = ?", (coin_id,)).fetchone()[0]
        return criptoID
    
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