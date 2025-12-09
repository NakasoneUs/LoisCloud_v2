import os
import time
import json
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# ============================
# LOAD ENV
# ============================
load_dotenv()

app = Flask(__name__)

# ============================
# CONFIG
# ============================
OPENROUTER_API = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "openai/gpt-4o-mini")
DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "128"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "25"))
DEFAULT_PROFILE = os.getenv("DEFAULT_PROFILE", "MORTAR").upper()

SYSTEM_PROFILES = {
    "MORTAR": """
Anda ialah LoisCloud v2 (Mortar Edition).
Gaya: tegas tapi mesra, straight to the point, fokus pada tindakan.
Bahasa: BM Malaysia (Negeri Sembilan). Elakkan Indonesia. Gaya bengkel bila sesuai.
""",

    "MENTOR": """
Anda ialah mentor peribadi. Nada profesional dan jelas.
Fokus memberi solusi yang tepat dan teratur.
""",

    "CHILL": """
Anda ialah kawan lepak yang bijak dari segala hal. Jawapan santai.
""",
}

DEFAULT_SYSTEM_MESSAGE = SYSTEM_PROFILES.get(DEFAULT_PROFILE, SYSTEM_PROFILES["MORTAR"])

SYSTEM_MESSAGE = DEFAULT_SYSTEM_MESSAGE


# ============================
# LOGGING
# ============================
def log(tag, obj):
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    try:
        payload = json.dumps(obj, ensure_ascii=False)
    except Exception:
        payload = str(obj)
    print(f"[{ts}] [{tag}] {payload}", flush=True)


# ============================
# ROUTE: /v1/chat/completions
# ============================
@app.route("/v1/chat/completions", methods=["POST"])
def chat():
    data = request.json

    messages = data.get("messages", [])
    model = data.get("model", DEFAULT_MODEL)
    max_tokens = data.get("max_tokens", DEFAULT_MAX_TOKENS)

    # LOG inbound
    log("INBOUND", data)

    # Masukkan system message yang dipilih
    full_messages = [{"role": "system", "content": SYSTEM_MESSAGE}] + messages

    payload = {
        "model": model,
        "messages": full_messages,
        "max_tokens": max_tokens
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }

    try:
        r = requests.post(
            OPENROUTER_API,
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        r.raise_for_status()
        result = r.json()

        log("UPSTREAM_RESPONSE", result)

        return jsonify(result), 200

    except Exception as e:
        log("ERROR", str(e))
        return jsonify({"error": str(e)}), 500


# ============================
# RUN SERVER
# ============================
if __name__ == "__main__":
    print(">> LoisCloud_Local ready.")
    app.run(host="0.0.0.0", port=5000)
