from flask import Flask, request, jsonify
import requests
import os

# ==========================
#  LoisCloud v2 – DeepSeek
# ==========================

DEEPSEEK_API = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")

if not DEEPSEEK_KEY:
    # Kalau error ni keluar dekat Render log, maknanya env var tak set
    raise RuntimeError("DEEPSEEK_API_KEY is not set in environment variables")


app = Flask(__name__)


# --------- Health check / status ----------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "engine": "LoisCloud_v2",
        "model": "deepseek-chat",
        "status": "online"
    })


# --------- Proxy endpoint ----------
@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    # Ambil JSON dari client
    data = request.get_json(force=True, silent=True) or {}

    messages = data.get("messages") or []
    if not isinstance(messages, list) or not messages:
        return jsonify({
            "error": "invalid_request",
            "message": "Field 'messages' mesti list dan tak boleh kosong"
        }), 400

    max_tokens = data.get("max_tokens", 512)
    temperature = data.get("temperature", 0.7)

    payload = {
        "model": "deepseek-chat",   # model utama DeepSeek
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_KEY}",
    }

    try:
        resp = requests.post(
            DEEPSEEK_API,
            json=payload,
            headers=headers,
            timeout=60
        )
    except requests.RequestException as e:
        # Kalau DeepSeek down / network problem
        return jsonify({
            "error": "upstream_request_error",
            "detail": str(e)
        }), 502

    # Kalau DeepSeek balas bukan 200
    if resp.status_code != 200:
        try:
            body = resp.json()
        except Exception:
            body = resp.text

        return jsonify({
            "error": "upstream_non_200",
            "status_code": resp.status_code,
            "body": body
        }), 502

    # Berjaya → pass-through je balik ke client
    return jsonify(resp.json())


if __name__ == "__main__":
    # Render akan hantar env PORT, tapi kita letak default 10000
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
