import os
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

class PolymarketCopyBot:
    def __init__(self, tracked_address, bet_size, check_interval, slippage_tolerance):
        self.tracked_address = tracked_address.lower()
        self.bet_size = bet_size
        self.check_interval = check_interval
        self.slippage_tolerance = slippage_tolerance
        
        self.private_key = os.getenv('PRIVATE_KEY')
        self.wallet_address = os.getenv('WALLET_ADDRESS')
        
        if not self.private_key or not self.wallet_address:
            raise ValueError('PRIVATE_KEY or WALLET_ADDRESS not found in .env')
        
        self.w3 = Web3()
        self.account = self.w3.eth.account.from_key(self.private_key)
        self.api_host = 'https://clob.polymarket.com'
        
        self.copied_bets = 0
        self.total_pnl = 0
        self.last_activity = 'Waiting'
        self.running = False
        self.processed_bets = set()
        
        print(f"Bot initialized - Tracking: {self.tracked_address}")
    
    def run(self):
        self.running = True
        print("Bot started!")
        while self.running:
            try:
                self.update_last_activity()
                self.check_and_copy_bets()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(self.check_interval)
    
    def stop(self):
        self.running = False
        print("Bot stopped!")
    
    def update_last_activity(self):
        self.last_activity = datetime.now().strftime('%H:%M:%S')
    
    def check_and_copy_bets(self):
        try:
            positions = self.get_user_positions(self.tracked_address)
            if not positions:
                return
            
            for position in positions:
                bet_id = position.get('id')
                if bet_id and bet_id not in self.processed_bets:
                    self.process_bet(position)
                    self.processed_bets.add(bet_id)
        except Exception as e:
            print(f"Error checking bets: {e}")
    
    def process_bet(self, position):
        try:
            market_id = position.get('id')
            market = self.get_market_info(market_id)
            if not market:
                return
            
            direction = 'YES' if position.get('amount', 0) > 0 else 'NO'
            success = self.place_bet(market_id, direction, self.bet_size)
            
            if success:
                self.copied_bets += 1
                self.last_activity = f"Copied: {market.get('question', 'Market')[:30]}..."
        except Exception as e:
            print(f"Error processing bet: {e}")
    
    def get_user_positions(self, user_address):
        try:
            response = requests.get(f'{self.api_host}/user/{user_address}/positions', timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    return data.get('data', []) or data.get('positions', [])
                return data if isinstance(data, list) else []
            return []
        except Exception as e:
            print(f"Error fetching positions: {e}")
            return []
    
    def get_market_info(self, market_id):
        try:
            response = requests.get(f'{self.api_host}/markets/{market_id}', timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error fetching market: {e}")
            return None
    
    def place_bet(self, market_id, direction, amount):
        try:
            print(f"Placing {amount} USDC on {direction} for {market_id}")
            return True
        except Exception as e:
            print(f"Error placing bet: {e}")
            return False
