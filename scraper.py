import requests
from requests.exceptions import *
from json import JSONDecodeError

def handle_error(e):
    if isinstance(e, requests.exceptions.RequestException):
        print(f"Network error: {e}")
    elif isinstance(e, JSONDecodeError):
        print("Error: Response was not valid JSON.")
    elif isinstance(e, KeyError):
        print(f"Error: Missing expected field in response: {e}")
    else: 
        print(f"An unexpected error occurred: {e}")


def get_data(url="https://api.hypixel.net/v2/skyblock/bazaar"): 
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data is not None:
            last_updated = data["lastUpdated"]
            products = data["products"]
            return products, last_updated
        
        return None
        
    except Exception as e:
        handle_error(e)

