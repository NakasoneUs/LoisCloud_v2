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
DEFAULT_MODEL = os.getenv("DEFAULT_PROFILE", "MORTAR") .upper()
SYSTEM PROFILES = {
    "MORTAR": """
Anda ialah LoisCloud v2 (Mortar Edition).
Gaya: tegas tapi mesra, straight to the point, fokus pada tindakan.
Bahasa: BM Malaysia (Negeri Sembilan). Elakan Indonesia. Gaya bengkel bila sesuai.
""",
    "MENTOR": """
Anda ialah mentor peribadi. Nada profesional dan jelas.
""",
    "CHILL": """
Anda ialah kawan lepak yang bijak dari segala hal. jawapan santai.
"""
}
DEFAULT_SYSTEM_MESSAGE = SYSTEM_PROFILES.get(DEFAULT_PROFILE, SYSTEM_PROFILES["MORTAR"]

SYSTEM_MESSAGE = DEFAULT_SYSTEM_MESSAGE
  
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
        return jsonify({"error": {"message": "Missing OPENROUTER_API_KEY"}}), 500

    data = request.json or {}

    user_messages = data.get("messages", [])
    if not isinstance(user_messages, list):
        return jsonify({"error": {"message": "messages must be a list"}}), 400

    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE},
        *user_messages
    ]

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            *messages
        ],
        "max_tokens": data.get("max_tokens", DEFAULT_MAX_TOKENS),
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENROUTER_KEY}"
    }

     log("INBOUND", {"model": model, "payload": payload})

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
                "message": f"Upstream error: {e}"}), 502
                "detail": str(e)

    try:
        out_json = r.json()
    except ValueError:
        # Kalau upstream balas text biasa
        return (r.text, r.status_code, {"Content-Type": "text/plain"})
 log("UPSTREAM_RESP", {"status": r.status_code, "json": out_json})

    return jsonify(out_json), r.status_code
    else:
        return (text_body, status, {"Content-Type": "text/plain"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)

