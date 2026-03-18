import os
import threading
from flask import Flask, jsonify, render_template, request
from bot import PolymarketCopyBot

app = Flask(__name__)


class BotManager:
    def __init__(self):
        self.bot = None
        self.thread = None
        self.lock = threading.Lock()

    def start(self, tracked_address, bet_size, check_interval, slippage_tolerance):
        with self.lock:
            if self.bot and self.bot.running:
                return False, 'Bot is already running'
            try:
                self.bot = PolymarketCopyBot(
                    tracked_address=tracked_address,
                    bet_size=float(bet_size),
                    check_interval=int(check_interval),
                    slippage_tolerance=float(slippage_tolerance),
                )
                self.thread = threading.Thread(target=self.bot.run, daemon=True)
                self.thread.start()
                return True, 'Bot started successfully'
            except Exception as e:
                return False, str(e)

    def stop(self):
        with self.lock:
            if not self.bot or not self.bot.running:
                return False, 'Bot is not running'
            self.bot.stop()
            return True, 'Bot stopped successfully'

    def status(self):
        with self.lock:
            if not self.bot:
                return {
                    'running': False,
                    'copied_bets': 0,
                    'total_pnl': 0.0,
                    'last_activity': 'Never',
                }
            return {
                'running': self.bot.running,
                'copied_bets': self.bot.copied_bets,
                'total_pnl': self.bot.total_pnl,
                'last_activity': self.bot.last_activity,
            }


bot_manager = BotManager()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/start', methods=['POST'])
def api_start():
    data = request.get_json() or {}
    tracked_address = data.get('tracked_address', '').strip()
    bet_size = data.get('bet_size', 10)
    check_interval = data.get('check_interval', 60)
    slippage_tolerance = data.get('slippage_tolerance', 0.5)

    if not tracked_address:
        return jsonify({'success': False, 'message': 'Tracked wallet address is required'}), 400

    success, message = bot_manager.start(
        tracked_address=tracked_address,
        bet_size=bet_size,
        check_interval=check_interval,
        slippage_tolerance=slippage_tolerance,
    )
    status_code = 200 if success else 400
    return jsonify({'success': success, 'message': message}), status_code


@app.route('/api/stop', methods=['POST'])
def api_stop():
    success, message = bot_manager.stop()
    status_code = 200 if success else 400
    return jsonify({'success': success, 'message': message}), status_code


@app.route('/api/status', methods=['GET'])
def api_status():
    return jsonify(bot_manager.status())


if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug)
