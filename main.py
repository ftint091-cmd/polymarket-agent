import os
import json
import requests
from dotenv import load_dotenv
from web3 import Web3
from eth_account.messages import encode_defunct
from datetime import datetime
import time

load_dotenv()

PRIVATE_KEY = os.getenv('PRIVATE_KEY')
WALLET_ADDRESS = os.getenv('WALLET_ADDRESS')
POLYMARKET_API = 'https://clob.polymarket.com'

if not PRIVATE_KEY or not WALLET_ADDRESS:
    raise ValueError('PRIVATE_KEY or WALLET_ADDRESS not found in .env file')

w3 = Web3()
account = w3.eth.account.from_key(PRIVATE_KEY)

print("=" * 60)
print("Polymarket Trading Bot")
print("=" * 60)
print(f"Wallet: {WALLET_ADDRESS}")
print(f"API: {POLYMARKET_API}")

def get_markets():
    """Get available markets from Polymarket"""
    try:
        print("\n📊 Fetching markets...")
        response = requests.get(
            f'{POLYMARKET_API}/markets?limit=10',
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Handle both list and dict responses
            if isinstance(data, dict):
                markets = data.get('data', []) or data.get('markets', [])
                if not markets:
                    markets = list(data.values())[:10]
            else:
                markets = data if isinstance(data, list) else []
            
            print(f"✅ Found {len(markets)} markets")
            return markets
        else:
            print(f"❌ Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def get_user_positions():
    """Get user's current positions"""
    try:
        print(f"\n💰 Fetching positions for {WALLET_ADDRESS}...")
        response = requests.get(
            f'{POLYMARKET_API}/user/{WALLET_ADDRESS}/positions',
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, dict):
                positions = data.get('data', []) or data.get('positions', [])
                if not positions:
                    positions = list(data.values())
            else:
                positions = data if isinstance(data, list) else []
            
            print(f"✅ Found {len(positions)} positions")
            return positions
        else:
            print(f"⚠️ No positions found or user not exists")
            return []
    except Exception as e:
        print(f"⚠️ Could not fetch positions: {e}")
        return []

def get_market_info(market_id):
    """Get info about specific market"""
    try:
        response = requests.get(
            f'{POLYMARKET_API}/markets/{market_id}',
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("\n" + "=" * 60)
    print("Starting Polymarket Bot")
    print("=" * 60)
    
    # Get markets
    markets = get_markets()
    if markets and len(markets) > 0:
        print("\n📈 Top Markets:")
        for i, market in enumerate(markets[:5], 1):
            if isinstance(market, dict):
                question = market.get('question', 'N/A')
                market_id = market.get('id', 'N/A')
            else:
                question = str(market)[:50]
                market_id = 'N/A'
            
            print(f"{i}. {str(question)[:50]}")
            print(f"   ID: {market_id}")
    else:
        print("\n⚠️ No markets found")
    
    # Get user positions
    positions = get_user_positions()
    if positions and len(positions) > 0:
        print(f"\n🎯 Your Positions: {len(positions)}")
        for i, pos in enumerate(positions[:3], 1):
            print(f"  {i}. {pos}")
    else:
        print(f"\n🎯 No positions found")
    
    print("\n✅ Bot running successfully!")

if __name__ == '__main__':
    main()