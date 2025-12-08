from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import time
import json

# =========================
# LOAD ENV
# =========================
load_dotenv()

app = Flask(__name__)

# =========================
# CONFIG
# =========================
OPENROUTER_API = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "openai/gpt-4o-mini")
DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "128"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "25"))

SYSTEM_MESSAGE = (
    "Kau adalah LoisCloud v2. Jawab dalam Bahasa Melayu Malaysia sahaja. "
    "Elakkan gaya Indonesia. Nada: direct, ringkas, gaya bengkel bila sesuai. "
    "Jangan beri jawapan panjang berjela. Fokus kepada poin penting sahaja."
)

def log(tag, obj):
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    try:
        payload = json.dumps(obj, ensure_ascii=False)
    except Exception:
        payload = str(obj)
    print(f"[{ts}] {tag}: {payload}", flush=True)

# =========================
# ROUTES
# =========================
@app.route("/", methods=["GET"])
def home():
    return {
        "engine": "LoisCloud_v2",
        "provider": "OpenRouter",
        "model": DEFAULT_MODEL,
        "status": "online"
    }

@app.route("/ping", methods=["GET"])
def ping():
    return {"status": "ok", "engine": "LoisCloud_v2"}, 200

@app.route("/v1/chat/completions", methods=["POST"])
def chat():
    if not OPENROUTER_KEY:
        return jsonify({"error": {"message": "Missing OPENROUTER_API_KEY"}}), 400

    data = request.json or {}

    user_messages = data.get("messages", [])
    if not isinstance(user_messages, list):
        return jsonify({"error": {"message": "messages must be a list"}}), 400

    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE},
        *user_messages
    ]

    payload = {
        "model": data.get("model", DEFAULT_MODEL),
        "messages": messages,
        "max_tokens": data.get("max_tokens", DEFAULT_MAX_TOKENS)
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENROUTER_KEY}"
    }

    log("INBOUND", {"payload": payload})

    try:
        r = requests.post(
            OPENROUTER_API,
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
    except requests.RequestException as e:
        log("ERROR_UPSTREAM", {"error": str(e)})
        return jsonify({
            "error": {
                "message": "Upstream request failed",
                "detail": str(e)
            }
        }), 502

    status = r.status_code
    text_body = r.text

    try:
        resp_json = r.json()
    except ValueError:
        resp_json = None

    log("UPSTREAM_RESP", {
        "status": status,
        "json": resp_json if resp_json is not None else text_body[:500]
    })

    if resp_json is not None:
        return jsonify(resp_json), status
    else:
        return (text_body, status, {"Content-Type": "text/plain"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
