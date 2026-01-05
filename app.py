import os, sys, requests, random
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
PUBLIC_DIR = os.path.join(BASE_DIR, '')  # Current directory for static files

sys.path.append(BASE_DIR)
import config_api as config

app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')
CORS(app)

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
    except Exception as e:
        print(f"Error fetching rates: {e}")
        rates = {}

@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/init-data')
def init_data():
    try:
        fetch_rates()
        
        print("Fetching crypto...")
        crypto_req = requests.get(config.CRYPTO_API, timeout=10)
        crypto_req.raise_for_status()
        crypto_data = crypto_req.json()
        print("Crypto fetched")
        
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
    app.run(debug=config.DEBUG, port=config.PORT)