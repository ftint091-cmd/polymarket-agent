from flask import Flask, render_template, request

app = Flask(__name__)

# Sample data structure to track accounts and bet amounts
tracked_accounts = []

@app.route('/')
def dashboard():
    return render_template('dashboard.html', accounts=tracked_accounts)

@app.route('/add_account', methods=['POST'])
def add_account():
    account_name = request.form['account_name']
    bet_amount = request.form['bet_amount']
    tracked_accounts.append({'name': account_name, 'bet': bet_amount})
    return render_template('dashboard.html', accounts=tracked_accounts)

if __name__ == '__main__':
    app.run(debug=True)