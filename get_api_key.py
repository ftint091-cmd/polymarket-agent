import os
import json
from dotenv import load_dotenv
from web3 import Web3
from eth_account.messages import encode_defunct
import requests
from datetime import datetime
import time

load_dotenv()

PRIVATE_KEY = os.getenv('PRIVATE_KEY')
POLYMARKET_API_HOST = 'https://clob.polymarket.com'

if not PRIVATE_KEY:
    raise ValueError('PRIVATE_KEY not found in .env file')

w3 = Web3()
account = w3.eth.account.from_key(PRIVATE_KEY)
wallet_address = account.address

print(f"Using wallet address: {wallet_address}")
print(f"Connecting to: {POLYMARKET_API_HOST}")

def create_api_key():
    now = str(int(time.time() * 1000))
    
    message_to_sign = wallet_address + now
    
    message = encode_defunct(text=message_to_sign)
    signed_message = account.sign_message(message)
    signature = signed_message.signature.hex()
    
    headers = {
        'POLY_ADDRESS': wallet_address,
        'POLY_SIGNATURE': signature,
        'POLY_TIMESTAMP': now,
        'POLY_NONCE': '0'
    }
    
    print("\nRequesting API credentials...")
    
    try:
        response = requests.post(
            f'{POLYMARKET_API_HOST}/auth/api-key',
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            credentials = response.json()
            print("\n✅ API credentials obtained!")
            return credentials
        else:
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def save_to_env(credentials):
    if not credentials:
        print("No credentials to save")
        return False
    
    env_path = '.env'
    
    with open(env_path, 'a') as f:
        f.write(f'\nPOLYMARKET_API_KEY={credentials.get("apiKey", "")}\n')
        f.write(f'POLYMARKET_SECRET={credentials.get("secret", "")}\n')
        f.write(f'POLYMARKET_PASSPHRASE={credentials.get("passphrase", "")}\n')
        f.write(f'WALLET_ADDRESS={wallet_address}\n')
    
    print(f"✅ Saved to {env_path}")
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("Polymarket API Key Generator")
    print("=" * 60)
    
    creds = create_api_key()
    
    if creds:
        save_to_env(creds)
        print("\n✅ All done!")
    else:
        print("\n❌ Failed")