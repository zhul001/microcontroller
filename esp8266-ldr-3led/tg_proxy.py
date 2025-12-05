# telegram_proxy_cors.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS untuk semua route

TELEGRAM_TOKEN = "token bot telegram"


@app.route('/', methods=['GET', 'POST', 'OPTIONS'])
def handle_request():
    if request.method == 'OPTIONS':
        # Handle preflight request
        return '', 200

    if request.method == 'GET':
        return jsonify({
            "status": "OK",
            "message": "Telegram Proxy Server Running",
            "endpoint": "POST JSON to this URL with chat_id and text"
        })

    # Handle POST from ESP
    try:
        # Try to get JSON data
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Content-Type must be application/json"
            }), 415

        data = request.get_json()

        # Debug print
        print(f"\n[PROXY] Received data: {data}")

        chat_id = str(data.get('chat_id')) if data.get('chat_id') else None
        message = data.get('text', '').strip()

        if not chat_id:
            return jsonify({
                "success": False,
                "error": "Missing or invalid chat_id"
            }), 400

        if not message:
            return jsonify({
                "success": False,
                "error": "Message text cannot be empty"
            }), 400

        print(f"[PROXY] Sending to chat_id: {chat_id}")
        print(f"[PROXY] Message: {message[:100]}...")

        # Forward to Telegram
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        telegram_data = {
            "chat_id": chat_id,
            "text": message
        }

        response = requests.post(telegram_url, json=telegram_data, timeout=10)

        print(f"[PROXY] Telegram response: {response.status_code}")

        if response.status_code == 200:
            return jsonify({
                "success": True,
                "message": "Forwarded to Telegram",
                "telegram_response": response.json()
            })
        else:
            error_msg = f"Telegram API error: {response.status_code}"
            print(f"[PROXY] {error_msg}")
            print(f"[PROXY] Details: {response.text}")
            return jsonify({
                "success": False,
                "error": error_msg,
                "details": response.text[:500]
            }), 500

    except Exception as e:
        print(f"[PROXY] Exception: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("TELEGRAM PROXY SERVER WITH CORS")
    print("=" * 60)
    app.run(host='0.0.0.0', port=8888, debug=True)
