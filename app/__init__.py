from flask import Flask
from stellar_sdk import Server

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

server = Server(horizon_url="https://horizon-testnet.stellar.org")
app.config['STELLAR_SERVER'] = server

from app import routes
