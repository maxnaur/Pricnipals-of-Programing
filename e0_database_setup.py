import os
import sqlite3 as sql
import bcrypt

def connect(dbLocation):
    """Connect to the SQLite database."""
    if not os.path.exists(dbLocation):
        open(dbLocation, 'w').close()
    connection = sql.connect(dbLocation)
    return connection

# Insert admin account
def Create_Admin(cursor):
    usernameOfAdmin = "admin"
    cursor.execute("SELECT Password FROM User WHERE Username = ?", (usernameOfAdmin,))
    foundPassword = cursor.fetchone()

    if foundPassword is None:
        AdminPassword = "admin"
        hashed_password = bcrypt.hashpw(AdminPassword.encode('utf-8'), bcrypt.gensalt())
        cursor.execute('''
            INSERT INTO User (Username, Email, Password, AccessLevel) 
            VALUES (?, ?, ?, ?)''',
            (usernameOfAdmin, "admin@hotmail.com", hashed_password, 1))
        
    # admin wallet should exist with some bitcoin
    cursor.execute("SELECT ID FROM User WHERE Username = ?", (usernameOfAdmin,))
    admin_row = cursor.fetchone()
    if admin_row is None:
        raise RuntimeError("Admin user not found after insertion")
    admin_id = admin_row[0]

    # Ensure Bitcoin exists. Use CoinID for uniqueness and query by CoinID.
    coin_id_value = "bitcoin"
    cursor.execute("SELECT ID FROM Crypto WHERE CoinID = ?", (coin_id_value,))
    crypto_row = cursor.fetchone()
    if crypto_row is None:
        cursor.execute('''
            INSERT INTO Crypto (Name, CoinID)
            VALUES (?, ?)''',
            ("Bitcoin", coin_id_value))
        cursor.execute("SELECT ID FROM Crypto WHERE CoinID = ?", (coin_id_value,))
        crypto_row = cursor.fetchone()

    if crypto_row is None:
        raise RuntimeError("Failed to create or find Crypto with CoinID 'bitcoin'")

    crypto_id = crypto_row[0]
    cursor.execute("SELECT * FROM Wallet WHERE UserID = ? AND CryptoID = ?", (admin_id, crypto_id))
    foundWallet = cursor.fetchone()
    if foundWallet is None:
        cursor.execute('''
            INSERT INTO Wallet (UserID, CryptoID, Amount) 
            VALUES (?, ?, ?)''',
            (admin_id, crypto_id, 10))

def setup_database(dbLocation):
    """Create all tables if they don't exist"""
    connection = connect(dbLocation)
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Username TEXT UNIQUE,
        Email TEXT,
        Password TEXT,
        AccessLevel INTEGER
    );''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Crypto (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT,
        CoinID TEXT UNIQUE
    );''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Wallet (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER,
        CryptoID INTEGER,
        Amount REAL,
        FOREIGN KEY(UserID) REFERENCES User(ID),
        FOREIGN KEY(CryptoID) REFERENCES Crypto(ID)
    );''')

    Create_Admin(cursor)

    connection.commit()
    connection.close()


