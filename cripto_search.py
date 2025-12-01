import requests
import random

def fetch_crypto_list(): # Fetch top 250 cryptos by market cap
    url = r"https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "x-cg-demo-api-key" : random.randint(100000,999999), # create random number for demo key so there will not be an output limit
        "vs_currency": "gbp", # pound
        "include_market_cap": "true", # include market cap data
        "order": "market_cap_desc", # order by market cap
        "per_page": 250, # number of results
    }
    
    response = requests.get(url, params)
    assert response.status_code == 200, "API request failed" # error handling
    return response.json()

def search_crypto(term): # Search for specific crypto
    url = r"https://api.coingecko.com/api/v3/search"
    params = {
        "x-cg-demo-api-key" : random.randint(100000,999999),
        "query": term # search term
        }
    response = requests.get(url, params) # will return top 100 results
    assert response.status_code == 200, "API request failed" # error handling
    return response.json()

def fetch_coin_details(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    params = {
        "x-cg-demo-api-key" : random.randint(100000,999999),
        "localization": "false",
        "tickers": "false",
        "market_data": "true",
        "community_data": "false",
        "developer_data": "false",
        "sparkline": "false"
    }
    response = requests.get(url, params)
    assert response.status_code == 200, "API request failed" # error handling
    return response.json()