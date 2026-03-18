import os
import requests
import time
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class PolymarketCopyBot:
    def __init__(self, tracked_address, bet_size, check_interval, slippage_tolerance):
        self.tracked_address = tracked_address.lower()
        self.bet_size = bet_size
        self.check_interval = check_interval
        self.slippage_tolerance = slippage_tolerance

        self.private_key = os.getenv('PRIVATE_KEY')
        self.wallet_address = os.getenv('WALLET_ADDRESS')

        # Demo mode when no wallet credentials are configured
        self.demo_mode = not (self.private_key and self.wallet_address)

        if self.demo_mode:
            print("[INFO] Running in DEMO mode (no PRIVATE_KEY/WALLET_ADDRESS configured)")
        else:
            print(f"[INFO] Running in LIVE mode - Wallet: {self.wallet_address}")

        self.data_api = 'https://data-api.polymarket.com'
        self.gamma_api = 'https://gamma-api.polymarket.com'
        self.copied_bets = 0
        self.total_pnl = 0.0
        self.last_activity = 'Waiting'
        self.running = False
        self.processed_trades = set()

        print(f"[INFO] Bot initialized - Tracking: {self.tracked_address}")

    def run(self):
        self.running = True
        mode = "DEMO" if self.demo_mode else "LIVE"
        print(f"[INFO] Bot started in {mode} mode!")

        while self.running:
            try:
                self.update_last_activity()
                self.monitor_trades()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"[ERROR] {e}")
                time.sleep(self.check_interval)

    def stop(self):
        self.running = False
        print("[INFO] Bot stopped!")

    def update_last_activity(self):
        self.last_activity = datetime.now().strftime('%H:%M:%S')

    def monitor_trades(self):
        """Monitor trades for the tracked address via data-api.polymarket.com"""
        try:
            print(f"[MONITOR] Checking trades for {self.tracked_address}")

            url = f'{self.data_api}/activity?user={self.tracked_address}&limit=50'
            print(f"[API] Requesting: {url}")

            response = requests.get(url, timeout=10)
            print(f"[API] Response status: {response.status_code}")

            if response.status_code != 200:
                print(f"[ERROR] API returned {response.status_code}: {response.text[:200]}")
                return

            data = response.json()
            trades = data if isinstance(data, list) else data.get('data', [])

            print(f"[TRADES] Found {len(trades)} recent trades")

            if not trades:
                return

            for trade in trades:
                trade_id = trade.get('id') or trade.get('transactionHash')

                if not trade_id:
                    print(f"[SKIP] Trade missing id and transactionHash, skipping")
                    continue

                if trade_id not in self.processed_trades:
                    print(f"[NEW TRADE] Detected: {trade_id}")
                    self.copy_trade(trade)
                    self.processed_trades.add(trade_id)

        except requests.exceptions.Timeout:
            print("[ERROR] API request timed out")
        except requests.exceptions.ConnectionError:
            print("[ERROR] Could not connect to Polymarket API")
        except Exception as e:
            print(f"[ERROR] monitoring trades: {e}")
            import traceback
            traceback.print_exc()

    def copy_trade(self, trade):
        """Log and copy a detected trade"""
        try:
            trade_id = trade.get('id') or trade.get('transactionHash')
            outcome = trade.get('outcome') or trade.get('side', 'Unknown')
            timestamp = trade.get('timestamp') or trade.get('createdAt', '')

            try:
                size = float(trade.get('usdcSize') or trade.get('size') or trade.get('amount') or self.bet_size)
            except (TypeError, ValueError):
                size = float(self.bet_size)

            try:
                price = float(trade.get('price') or 0)
            except (TypeError, ValueError):
                price = 0.0

            market_id = trade.get('market') or trade.get('conditionId', '')
            question = trade.get('question') or trade.get('title') or market_id

            print(f"[COPY] -------- Trade Details --------")
            print(f"[COPY] ID:        {trade_id}")
            print(f"[COPY] Market:    {question}")
            print(f"[COPY] Side:      {outcome}")
            print(f"[COPY] Size:      {size:.2f} USDC")
            print(f"[COPY] Price:     {price:.4f}")
            if timestamp:
                print(f"[COPY] Time:      {timestamp}")
            print(f"[COPY] ----------------------------------")

            success = self.place_bet(market_id, outcome, size, price)

            if success:
                self.copied_bets += 1
                self.last_activity = f"Copied {outcome}"
                print(f"[SUCCESS] Trade copied! Total: {self.copied_bets}")
            else:
                print(f"[FAILED] Could not copy trade")

        except Exception as e:
            print(f"[ERROR] copying trade: {e}")
            import traceback
            traceback.print_exc()

    def place_bet(self, market_id, direction, amount, price=0):
        """Place a bet on a market (demo or live)"""
        try:
            print(f"[BET] Placing {amount:.2f} USDC on '{direction}' for market {market_id}")

            if self.demo_mode:
                print(f"[BET] DEMO MODE - Trade detected and logged, no real order placed")
                return True

            # Real order placement requires PRIVATE_KEY and WALLET_ADDRESS
            print(f"[BET] LIVE MODE - Real order placement via CLOB API")
            # Real order placement is a future extension; for now log and return False
            print(f"[BET] Real order placement not yet implemented")
            return False

        except Exception as e:
            print(f"[ERROR] placing bet: {e}")
            return False

    def get_market_info(self, market_id):
        """Get market information from Gamma API"""
        try:
            url = f'{self.gamma_api}/markets/{market_id}'
            print(f"[API] Fetching market: {url}")
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                print(f"[API] Got market info")
                return response.json()

            print(f"[API] Market error: {response.status_code}")
            return None
        except Exception as e:
            print(f"[ERROR] fetching market: {e}")
            return None
