from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from bot import PolymarketCopyBot
import threading
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

class BotManager:
    def __init__(self):
        self.bot = None
        self.running = False
        self.thread = None
        self.stats = {
            'copied_bets': 0,
            'total_pnl': 0,
            'last_activity': 'Waiting',
            'last_log': None
        }
    
    def start(self, tracked_address, bet_size, check_interval, slippage_tolerance):
        if self.running:
            return False, "Bot already running"
        
        try:
            self.bot = PolymarketCopyBot(
                tracked_address=tracked_address,
                bet_size=bet_size,
                check_interval=check_interval,
                slippage_tolerance=slippage_tolerance
            )
            self.running = True
            self.thread = threading.Thread(target=self._run_bot, daemon=True)
            self.thread.start()
            return True, "Bot started successfully"
        except Exception as e:
            return False, str(e)
    
    def _run_bot(self):
        try:
            self.bot.run()
        except Exception as e:
            print(f"Bot error: {e}")
            self.running = False
    
    def stop(self):
        if self.bot and self.running:
            self.bot.stop()
            self.running = False
            return True, "Bot stopped"
        return False, "Bot not running"
    
    def get_stats(self):
        if self.bot and self.running:
            self.stats['copied_bets'] = self.bot.copied_bets
            self.stats['total_pnl'] = self.bot.total_pnl
            self.stats['last_activity'] = self.bot.last_activity
        
        return {
            'running': self.running,
            **self.stats
        }

bot_manager = BotManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def api_start():
    data = request.json
    
    tracked_address = data.get('tracked_address')
    bet_size = float(data.get('bet_size', 100))
    check_interval = int(data.get('check_interval', 5))
    slippage_tolerance = float(data.get('slippage_tolerance', 2))
    
    success, message = bot_manager.start(
        tracked_address,
        bet_size,
        check_interval,
        slippage_tolerance
    )
    
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'error': message}), 400

@app.route('/api/stop', methods=['POST'])
def api_stop():
    success, message = bot_manager.stop()
    return jsonify({'success': success, 'message': message})

@app.route('/api/status', methods=['GET'])
def api_status():
    return jsonify(bot_manager.get_stats())

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
