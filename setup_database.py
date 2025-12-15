import os
import sqlite3 as sql
import bcrypt

def find_ID(cursor, table, PrimaryKey, search_Item):
    """Connect to a table entered to get the Primary key"""
    cursor.execute(f"SELECT ID FROM {table} WHERE {PrimaryKey} = ?", (search_Item,))
    ID_List = cursor.fetchone()
    return ID_List

# -------------------------- add user -------------------------
def Add_User(cursor, username, password):
    """Add a user to the database"""
    ID_list = find_ID(cursor, "User", "Username", username)

    if ID_list is None: # if the ID doesn't exitst add a user
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute('''
            INSERT INTO User (Username, Email, Password, AccessLevel) 
            VALUES (?, ?, ?, ?)''',
            (username, f"{username}@hotmail.com", hashed_password, 1))
        ID_list = find_ID(cursor, "User", "Username", username)
    ID = ID_list[0]
    return ID

# -------------------------- add coins -------------------------
def Add_Coins(cursor, WALLET, API_Search):
    """Add all crypto currencys to the database"""
    # Fetch all crypto names in a single API call
    crypto_data = API_Search.fetch_crypto_batch(list(WALLET.keys()))
    crypto_ID_List = []

    for coin_id, _ in WALLET.items():
        ID_List = find_ID(cursor, "Crypto", "CoinID", coin_id)
        
        if ID_List is None:
            # Get name from batch data
            coin_name = crypto_data[coin_id].get('name')
            cursor.execute('''
                INSERT INTO Crypto (Name, CoinID)
                VALUES (?, ?)''',
                (coin_name, coin_id))
            ID_List = find_ID(cursor, "Crypto", "CoinID", coin_id)
        ID = ID_List[0]
        crypto_ID_List.append(ID)
    return crypto_ID_List

# -------------------------- add wallet -------------------------
def Add_Wallet(cursor, User_ID, crypto_ID_List, WALLET):
    """Add every crypto currency and the ammount to the bummy account wallet"""
    pointer = 0
    for _, amount in WALLET.items():
        crypto_ID = crypto_ID_List[pointer]
        # Check if wallet entry already exists
        cursor.execute("SELECT Amount FROM Wallet WHERE UserID = ? AND CryptoID = ?", (User_ID, crypto_ID))
        Amount_List = cursor.fetchone()
        
        if Amount_List is None:
            cursor.execute('''
                INSERT INTO Wallet (UserID, CryptoID, Amount) 
                VALUES (?, ?, ?)''',
                (User_ID, crypto_ID, amount))
        pointer += 1
    

def Create_Shown_User(cursor, API_Search): # username : user password : user
    """Add User dummy user"""
    username = "user"
    password = "user"
    WALLET = {
        'bitcoin': 0.5,
        'ethereum': 2,
        'tether': 1000,
        'binancecoin': 1,
        'solana': 10,
        'ripple': 500,
        'cardano': 1000,
        'dogecoin': 3000,
        'polkadot': 50,
        'litecoin': 5,
    }

    User_ID = Add_User(cursor, username, password)
    crypto_ID_List = Add_Coins(cursor, WALLET, API_Search)
    Add_Wallet(cursor, User_ID, crypto_ID_List, WALLET)


def Create_Admin(cursor, API_Search): # username : admin password : admin
    """Add admin dummy user"""
    username = "admin"
    password = "admin"
    WALLET = {
        'bitcoin': 10,
    }

    User_ID = Add_User(cursor, username, password)
    crypto_ID_List = Add_Coins(cursor, WALLET, API_Search)
    Add_Wallet(cursor, User_ID, crypto_ID_List, WALLET)


# ---------------------- function that will run first -------------------
def setup_database(dbLocation, API_Search):
    """Create database and all tables if they don't exist"""
    if not os.path.exists(dbLocation):
        open(dbLocation, 'w').close()
    connection = sql.connect(dbLocation, timeout=10.0) # time out
    cursor = connection.cursor()

    # create user table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Username TEXT UNIQUE,
        Email TEXT,
        Password TEXT,
        AccessLevel INTEGER
    );''')

    # create crypto identifyers
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Crypto (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT,
        CoinID TEXT UNIQUE
    );''')

    # create Wallet
    # a connected database for User and Crypto
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Wallet (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER,
        CryptoID INTEGER,
        Amount REAL,
        FOREIGN KEY(UserID) REFERENCES User(ID),
        FOREIGN KEY(CryptoID) REFERENCES Crypto(ID)
    );''')

    # create Transactions Log for User to User
    cursor.execute('''         
        CREATE TABLE IF NOT EXISTS Transactions_UserToUser (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        CryptoID INTEGER,
        UserFromID INTEGER,
        UserToID INTEGER,
        Amount REAL,
        DateTime TEXT,
        FOREIGN KEY(UserFromID) REFERENCES User(ID),
        FOREIGN KEY(UserToID) REFERENCES User(ID),
        FOREIGN KEY(CryptoID) REFERENCES Crypto(ID)
    );''')
    
    # create Transactions Log for Purchasing Crypto
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Transactions_Buy (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        CryptoID INTEGER,
        UserID INTEGER,
        Amount REAL,
        DateTime TEXT,
        FOREIGN KEY(UserID) REFERENCES User(ID),
        FOREIGN KEY(CryptoID) REFERENCES Crypto(ID)
    );''')

    # create Transactions Log for Selling Crypto
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Transactions_Sell (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        CryptoID INTEGER,
        UserID INTEGER,
        Amount REAL,
        DateTime TEXT,
        FOREIGN KEY(UserID) REFERENCES User(ID),
        FOREIGN KEY(CryptoID) REFERENCES Crypto(ID)
    );''')

    Create_Shown_User(cursor, API_Search)
    Create_Admin(cursor, API_Search)

    connection.commit()
    connection.close()
