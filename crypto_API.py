import requests
import random
from datetime import datetime, timezone
from CTkMessagebox import CTkMessagebox

# using CoinGecko
# limit of 5 - 15 calls per minute
# to stay safe only call every 12 seconds
# break down of every call
# setup_datablse 2 call
# m2_wallet 1 call for all coins, will break if over 100 coins in system for a user

class API_search():
    def __init__(self):
        self.call_list = []
        self.cash_top_250 = {}
        self.cash_top_250_last_call = None
        self.cash_wallet_coinIDs = None
        self.cash_wallet = {}
        self.cash_wallet_last_call = None

    def check_last_call(self):
        """make sure api is not called more than 6 times per minute"""
        current_time = datetime.now(timezone.utc)
        if len(self.call_list) > 4: # only find 5 calls per minute
            earlyest_time = self.call_list[0]
            diff_seconds = (current_time - earlyest_time).total_seconds()
            if diff_seconds > 60:
                self.call_list.pop(0)
            else:
                print(f"ran out of api calls wait {diff_seconds} seconds")
                CTkMessagebox(title="API Calls", message=f"ran out of api calls wait {diff_seconds} seconds", icon="close")
                return True
        self.call_list.append(current_time)
        return False
    
    def request(self, url, params):
        try:
            response = requests.get(url, params, timeout=10)
            assert response.status_code == 200, "API request failed" # error handling
            data = response.json()
            return data
        except Exception as e:
            # Log or handle the error (optional)
            print(f"Error fetching data: {e}")
            return {}

    def check_cash(self, last_called, cash):
        current_time = datetime.now(timezone.utc)
        diff_seconds = (current_time - last_called).total_seconds()
        if diff_seconds < 60:
            return True, cash
        else:
            return False, {}

    # in order of call throughout coded
    def fetch_crypto_batch(self, coin_ids):
        """Fetch coin data (names, prices, market data) for a list of coin IDs in a single API call."""
        # check cash if the wallet has been called before
        if self.cash_wallet_coinIDs == coin_ids:
            (cash, data) = self.check_cash(self.cash_wallet_last_call, self.cash_wallet)
            if cash:
                return data
        
        if self.check_last_call():
            return {}
        
        ids_str = ",".join(str(cid) for cid in coin_ids)
        url = r"https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "x-cg-demo-api-key": random.randint(100000, 999999),
            "vs_currency": "gbp",
            "ids": ids_str,
            "per_page": max(1, len(coin_ids)),
            "include_market_cap": "true",
            "sparkline": "false"
        }
        
        data = self.request(url, params)
        
        # Build mapping of coin_id to full market data
        batch_data = {}
        for coin in data:
            coin_id = coin.get('id')
            if coin_id:
                batch_data[coin_id] = {
                    'name': coin.get('name'),
                    'symbol': coin.get('symbol'),
                    'current_price': coin.get('current_price'),
                    'market_cap': coin.get('market_cap'),
                    'market_cap_rank': coin.get('market_cap_rank'),
                    'price_change_percentage_24h': coin.get('price_change_percentage_24h'),
                    'market_data': coin  # full data available if needed
                }
        
        self.cash_wallet_coinIDs = coin_ids
        self.cash_wallet_last_call = datetime.now(timezone.utc)
        self.cash_wallet = batch_data
        return self.cash_wallet
        
    def fetch_top_250_crypto_list(self): # Fetch top 250 cryptos by market cap
        (cash, data) = self.check_cash(self.cash_top_250_last_call, self.cash_top_250)
        if cash:
            return data

        if self.check_last_call():
            return {}
        
        url = r"https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "x-cg-demo-api-key" : random.randint(100000,999999), # create random number for demo key so there will not be an output limit
            "vs_currency": "gbp", # pound
            "include_market_cap": "true", # include market cap data
            "order": "market_cap_desc", # order by market cap
            "per_page": 250, # number of results
        }
        
        data = self.request(url, params)
        return data

    def search_crypto(self, term): # Search for specific crypto
        if self.check_last_call():
            return {}
        url = r"https://api.coingecko.com/api/v3/search"
        params = {
            "x-cg-demo-api-key" : random.randint(100000,999999),
            "query": term # search term
            }
        
        self.cash_top_250 = self.request(url, params)
        self.cash_top_250_last_call = datetime.now(timezone.utc)
        return self.cash_top_250
    
    def fetch_single_coin_details(self, coin_id):
        if self.check_last_call():
            return {}
        
        url = r"https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "x-cg-demo-api-key" : random.randint(100000,999999),
            'localization': 'false',
            'tickers': 'false',
            'market_data': 'true',
            'community_data': 'false',
            'developer_data': 'false',
            'sparkline': 'false'
        }
        
        data = self.request(url, params)
        return data

    def fetch_year_coin_history(self, coin_id):
        if self.check_last_call():
            return {}
        
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {
            'vs_currency': 'gbp', 
            'days': 365,
            'interval': 'daily'
        }
        data = self.request(url, params)
        return data.get('prices')

