import os, sys, requests, random
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
PUBLIC_DIR = os.path.join(BASE_DIR, '')  # Current directory for static files

sys.path.append(BASE_DIR)
import config_api as config

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# MongoDB connection
client = MongoClient("mongodb+srv://mudassar:Mudassar%4012345@currencyconverterapp.coai2fd.mongodb.net/?appName=CurrencyConverterApp")
db = client["CurrencyConverterApp"]
currencies_collection = db["currencies"]
crypto_collection = db["crypto"]

def save_rates_to_db(rates):
    try:
        # Clear old data
        currencies_collection.delete_many({})
        # Insert new data
        documents = [{"code": code, "rate": rate, "last_updated": datetime.utcnow()} for code, rate in rates.items()]
        currencies_collection.insert_many(documents)
        print(f"Saved {len(rates)} currencies to MongoDB")
    except Exception as e:
        print(f"Error saving rates to MongoDB: {e}")

def save_crypto_to_db(crypto_data):
    try:
        # Clear old data
        crypto_collection.delete_many({})
        # Insert new data
        documents = [{"id": id, "usd": data.get('usd', 0), "usd_24h_change": data.get('usd_24h_change', 0), "last_updated": datetime.utcnow()} for id, data in crypto_data.items()]
        crypto_collection.insert_many(documents)
        print(f"Saved {len(crypto_data)} crypto entries to MongoDB")
    except Exception as e:
        print(f"Error saving crypto to MongoDB: {e}")

def load_rates_from_db():
    try:
        documents = currencies_collection.find({}, {"_id": 0, "code": 1, "rate": 1})
        return {doc["code"]: doc["rate"] for doc in documents}
    except Exception as e:
        print(f"Error loading rates from MongoDB: {e}")
        return {}

def load_crypto_from_db():
    try:
        documents = crypto_collection.find({}, {"_id": 0, "id": 1, "usd": 1, "usd_24h_change": 1})
        return {doc["id"]: {"usd": doc["usd"], "usd_24h_change": doc["usd_24h_change"]} for doc in documents}
    except Exception as e:
        print(f"Error loading crypto from MongoDB: {e}")
        return {}

rates = {}

def fetch_rates():
    global rates
    try:
        curr_req = requests.get(f"{config.CURRENCY_API}/USD", timeout=10)
        curr_req.raise_for_status()
        curr_data = curr_req.json()
        rates = curr_data.get('rates', {})
        rates['USD'] = 1.0  # Ensure USD is 1
        print(f"Rates fetched: {len(rates)} currencies")
        # Load step: Save to database
        save_rates_to_db(rates)
    except Exception as e:
        print(f"Error fetching rates: {e}")
        rates = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/init-data')
def init_data():
    try:
        # Try to load from DB first
        cached_rates = load_rates_from_db()
        cached_crypto = load_crypto_from_db()
        
        if cached_rates:
            rates.update(cached_rates)
            print("Loaded rates from database")
        else:
            fetch_rates()
        
        if cached_crypto:
            crypto_data = cached_crypto
            print("Loaded crypto from database")
        else:
            print("Fetching crypto...")
            crypto_req = requests.get(config.CRYPTO_API, timeout=10)
            crypto_req.raise_for_status()
            crypto_data = crypto_req.json()
            print("Crypto fetched")
            # Load step: Save to database
            save_crypto_to_db(crypto_data)
        
        return jsonify({"currencies": rates, "crypto": crypto_data})
    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        return jsonify({"error": f"API request failed: {str(e)}"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route('/api/convert')
def convert():
    try:
        amt = float(request.args.get('amount', 1))
        frm = request.args.get('from', 'USD')
        to = request.args.get('to', 'PKR')
        
        print(f"Converting {amt} {frm} to {to}")
        
        if not rates:
            fetch_rates()
            if not rates:
                raise ValueError("Unable to fetch rates")
        
        if frm not in rates or to not in rates:
            raise ValueError(f"Invalid currency code: {frm} or {to}")
        
        if frm == 'USD':
            rate = rates[to]
        else:
            rate = rates[to] / rates[frm]
        
        # Transform: Simulate 10-point Trend Graph data
        trend = [round(rate * (1 + random.uniform(-0.02, 0.02)), 4) for _ in range(10)]
        
        print(f"Conversion result: {amt * rate}")
        return jsonify({
            "success": True,
            "result": round(amt * rate, 2),
            "rate": round(rate, 4),
            "trend": trend,
            "to_code": to
        })
    except ValueError as e:
        print(f"Value error: {e}")
        return jsonify({"success": False, "error": str(e)})
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"success": False, "error": f"Unexpected error: {str(e)}"})

if __name__ == '__main__':
    # Load rates on startup from MongoDB
    cached_rates = load_rates_from_db()
    if cached_rates:
        rates.update(cached_rates)
        print("Loaded rates from MongoDB on startup")
    app.run(debug=config.DEBUG, port=config.PORT)