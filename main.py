from flask import Flask, request, jsonify
import requests
import os
from flask_cors import CORS   # <-- untuk HTML tester / browser

app = Flask(__name__)
CORS(app)  # <-- kalau tak nak HTML tester, boleh buang baris ni

OPENROUTER_API = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return {
        "engine": "LoisCloud_v2",
        "provider": "OpenRouter",
        "model": "meta-llama/llama-3.2-3b-instruct:free",
        "status": "online"
    }

@app.route("/v1/chat/completions", methods=["POST"])
def chat():
    data = request.json

    payload = {
        "model": "meta-llama/llama-3.2-3b-instruct:free",
        "messages": data.get("messages", []),
        "max_tokens": data.get("max_tokens", 200)
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        # optional tapi bagus letak
        "HTTP-Referer": "https://loiscloud-v2.onrender.com",
        "X-Title": "LoisCloud_v2"
    }

    r = requests.post(OPENROUTER_API, json=payload, headers=headers)
    return jsonify(r.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
