from CTkMessagebox import CTkMessagebox
import sqlite3 as sql
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
    









    def close(self):
        self.db.close()