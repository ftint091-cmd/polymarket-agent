import os
import requests
import time
import json
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
        
        self.w3 = Web3(Web3.HTTPProvider('https://polygon-rpc.com'))
        self.account = self.w3.eth.account.from_key(self.private_key)
        
        self.api_host = 'https://gamma-api.polymarket.com'
        self.copied_bets = 0
        self.total_pnl = 0.0
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
                self.monitor_trades()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(self.check_interval)
    
    def stop(self):
        self.running = False
        print("Bot stopped!")
    
    def update_last_activity(self):
        self.last_activity = datetime.now().strftime('%H:%M:%S')
    
    def monitor_trades(self):
        """Мониторим ставки отслеживаемого адреса"""
        try:
            print(f"[MONITOR] Checking trades for {self.tracked_address}")
            
            # Получаем последние ставки через Gamma API
            url = f'{self.api_host}/trades?user={self.tracked_address}&limit=50'
            print(f"[API] Requesting: {url}")
            
            response = requests.get(url, timeout=10)
            print(f"[API] Response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"[ERROR] API returned {response.status_code}")
                print(f"[ERROR] Response: {response.text[:200]}")
                return
            
            data = response.json()
            print(f"[DEBUG] Response data: {json.dumps(data)[:300]}")
            
            trades = data.get('data', []) if isinstance(data, dict) else data
            
            print(f"[TRADES] Found {len(trades)} recent trades")
            
            if not trades:
                return
            
            for trade in trades:
                trade_id = trade.get('id')
                
                if trade_id and trade_id not in self.processed_bets:
                    print(f"[NEW TRADE] {trade_id}")
                    self.copy_trade(trade)
                    self.processed_bets.add(trade_id)
        
        except Exception as e:
            print(f"Error monitoring trades: {e}")
            import traceback
            traceback.print_exc()
    
    def copy_trade(self, trade):
        """Копируем ставку"""
        try:
            trade_id = trade.get('id')
            market = trade.get('market', {})
            market_id = market.get('id') if isinstance(market, dict) else market
            outcome = trade.get('outcome')
            amount = float(trade.get('amount', self.bet_size))
            
            print(f"[COPY] Trade ID: {trade_id}")
            print(f"[COPY] Market: {market_id}")
            print(f"[COPY] Outcome: {outcome}, Amount: {amount}")
            
            # Копируем ставку
            success = self.place_bet(market_id, outcome, amount)
            
            if success:
                self.copied_bets += 1
                self.last_activity = f"Copied {outcome}"
                print(f"[SUCCESS] Bet copied! Total copied: {self.copied_bets}")
            else:
                print(f"[FAILED] Could not copy trade")
        
        except Exception as e:
            print(f"Error copying trade: {e}")
            import traceback
            traceback.print_exc()
    
    def place_bet(self, market_id, direction, amount):
        """Размещаем ставку на рынке"""
        try:
            print(f"[BET] Placing {amount} USDC on {direction} for market {market_id}")
            
            # TODO: Реальное размещение ставки через API
            # Здесь нужно:
            # 1. Получить данные рынка
            # 2. Создать ордер
            # 3. Подписать транзакцию приватным ключом
            # 4. Отправить на CLOB
            
            # На данный момент просто возвращаем True для демонстрации
            print(f"[BET] Bet placed successfully (demo mode)")
            return True
        
        except Exception as e:
            print(f"Error placing bet: {e}")
            return False
    
    def get_market_info(self, market_id):
        """Получить информацию о рынке"""
        try:
            url = f'{self.api_host}/markets/{market_id}'
            print(f"[API] Fetching market: {url}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"[API] Got market info")
                return response.json()
            
            print(f"[API] Market error: {response.status_code}")
            return None
        except Exception as e:
            print(f"Error fetching market: {e}")
            return None
