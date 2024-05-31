from flask import render_template, request, jsonify
from app import app, server
from stellar_sdk import Keypair, TransactionBuilder, Network
import sqlite3

# Database setup
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    public_key TEXT,
                    secret TEXT,
                    balance REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS charities (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    address TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS donations (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    charity_id INTEGER,
                    amount REAL,
                    tx_id TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM charities")
    charities = c.fetchall()
    conn.close()
    return render_template('index.html', charities=charities)

@app.route('/convert', methods=['POST'])
def convert():
    amount = float(request.json['amount'])
    pair = Keypair.random()
    response = server.friendbot(pair.public_key).call()
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (public_key, secret, balance) VALUES (?, ?, ?)", (pair.public_key, pair.secret, amount))
    conn.commit()
    conn.close()
    return jsonify({"public_key": pair.public_key, "secret": pair.secret})

@app.route('/donate', methods=['POST'])
def donate():
    public_key = request.json['public_key']
    charity_id = request.json['charity_id']
    amount = float(request.json['amount'])
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT secret FROM users WHERE public_key = ?", (public_key,))
    secret = c.fetchone()[0]
    c.execute("SELECT address FROM charities WHERE id = ?", (charity_id,))
    charity_address = c.fetchone()[0]

    source_account = server.load_account(account_id=public_key)
    keypair = Keypair.from_secret(secret)
    transaction = TransactionBuilder(
        source_account=source_account,
        network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
        base_fee=100) \
        .add_text_memo("Donation to Charity") \
        .append_payment_op(charity_address, str(amount), "XLM") \
        .set_timeout(30) \
        .build()
    transaction.sign(keypair)
    response = server.submit_transaction(transaction)

    c.execute("INSERT INTO donations (user_id, charity_id, amount, tx_id) VALUES ((SELECT id FROM users WHERE public_key = ?), ?, ?, ?)",
              (public_key, charity_id, amount, response['hash']))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "tx_id": response['hash']})
