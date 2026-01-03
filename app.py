import os, sys, requests, random
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
PUBLIC_DIR = os.path.join(PROJECT_ROOT, 'templates')

sys.path.append(PROJECT_ROOT)
from app_settings import config_api as config

app = Flask(__name__, static_folder=PUBLIC_DIR, static_url_path='')
CORS(app)

@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/init-data')
def init_data():
    try:
        print("Fetching currencies...")
        curr_req = requests.get(f"{config.CURRENCY_API}/USD", timeout=10)
        curr_req.raise_for_status()
        curr_data = curr_req.json()
        print(f"Currencies fetched: {len(curr_data.get('rates', {}))} rates")
        
        print("Fetching crypto...")
        crypto_req = requests.get(config.CRYPTO_API, timeout=10)
        crypto_req.raise_for_status()
        crypto_data = crypto_req.json()
        print("Crypto fetched")
        
        return jsonify({"currencies": curr_data.get('rates', {}), "crypto": crypto_data})
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
        r = requests.get(f"{config.CURRENCY_API}/{frm}", timeout=10)
        r.raise_for_status()
        data = r.json()
        
        if 'rates' not in data or to not in data['rates']:
            raise ValueError(f"Invalid currency code: {to}")
        
        rate = data['rates'][to]
        
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
    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        return jsonify({"success": False, "error": f"API request failed: {str(e)}"})
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"success": False, "error": f"Unexpected error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=config.DEBUG, port=config.PORT)