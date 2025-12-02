from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

DEEPSEEK_API = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return {
        "engine": "LoisCloud_v2",
        "model": "deepseek/deepseek-r1:free",
        "status": "online"
    }

@app.route("/v1/chat/completions", methods=["POST"])
def chat():
    data = request.json

    payload = {
        "model": "deepseek-chat",
        "messages": data.get("messages", []),
        "max_tokens": data.get("max_tokens", 100)
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_KEY}"
    }

    r = requests.post(DEEPSEEK_API, json=payload, headers=headers)
    return jsonify(r.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
