from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# ====== CONFIG: OPENROUTER ======
OPENROUTER_API = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")  # ambil dari Environment Render

# Model default (free tier)
DEFAULT_MODEL = "deepseek/deepseek-r1:free"
DEFAULT_MAX_TOKENS = 64


# ====== HEALTH CHECK (ROOT) ======
@app.route("/", methods=["GET"])
def home():
    return {
        "engine": "LoisCloud_v2",
        "provider": "OpenRouter",
        "model": DEFAULT_MODEL,
        "status": "online"
    }


# ====== MAIN CHAT ENDPOINT ======
@app.route("/v1/chat/completions", methods=["POST"])
def chat():
    if not OPENROUTER_KEY:
        return jsonify({
            "error": {
                "type": "config_error",
                "message": "OPENROUTER_API_KEY is not set on server"
            }
        }), 500

    data = request.get_json(force=True, silent=True) or {}

    messages = data.get("messages", [])
    model = data.get("model", DEFAULT_MODEL)
    max_tokens = int(data.get("max_tokens", DEFAULT_MAX_TOKENS))

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        # optional tapi elok ada untuk OpenRouter
        "HTTP-Referer": "https://loiscloud-v2.onrender.com",
        "X-Title": "LoisCloud_v2"
    }

    try:
        r = requests.post(OPENROUTER_API, json=payload, headers=headers, timeout=60)
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": {
                "type": "network_error",
                "message": str(e)
            }
        }), 502

    # Kalau OpenRouter balas selain 200, kita pass balik error dia
    if r.status_code != 200:
        try:
            body = r.json()
        except ValueError:
            body = {"raw": r.text}

        return jsonify({
            "error": {
                "type": "upstream_error",
                "status_code": r.status_code,
                "body": body
            }
        }), 500

    try:
        resp_json = r.json()
    except ValueError:
        return jsonify({
            "error": {
                "type": "parse_error",
                "raw": r.text
            }
        }), 500

    return jsonify(resp_json)


if __name__ == "__main__":
    # Untuk local test je, Render pakai gunicorn
    app.run(host="0.0.0.0", port=10000)

