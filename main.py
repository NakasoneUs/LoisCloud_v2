from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv  # <-- tambah ni

load_dotenv()  # <-- dan ni, supaya .env dibaca

app = Flask(__name__)

# ========================
# OPENROUTER CONFIG
# ========================
OPENROUTER_API = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

DEFAULT_MODEL = "openai/gpt-4o-mini"
DEFAULT_MAX_TOKENS = 128

@app.route("/", methods=["GET"])
def home():
    return {
        "engine": "LoisCloud_v2",
        "provider": "OpenRouter",
        "model": DEFAULT_MODEL,
        "status": "online"
    }

@app.route("/v1/chat/completions", methods=["POST"])
def chat():
    if not OPENROUTER_KEY:
        return jsonify({"error": {"message": "Missing OPENROUTER_API_KEY"}}), 400

    data = request.json

    payload = {
        "model": data.get("model", DEFAULT_MODEL),
        "messages": [
            {
                "role": "system",
                "content": (
                  "Anda adalah pembantu yang hanya bercakap dalam Bahasa Melayu Malaysia (dialek Negeri Sembilan)."
                  "Jangan gunakan Bahasa Indonesia. Nada: mesra, manja, ringkas dan jelas. "
                  "Contoh: User: 'Apa khabar?' -> Assistant: 'Khabar baik, terima kasih. Apa yang boleh saya bantu hari ini?'"
              )  
            },
            *data.get("messages", [])
        ],
        "max_tokens": data.get("max_tokens", DEFAULT_MAX_TOKENS)
    }

    headers = {
        "Content-Type": "application/json",
