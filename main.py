import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# =========================
#  Config OpenRouter
# =========================
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

if not OPENROUTER_API_KEY:
    # Kalau lupa set API key dalam Render, terus bagi error masa boot
    raise RuntimeError("OPENROUTER_API_KEY not set in environment variables")

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://loiscloud-v2.onrender.com",
    "X-Title": "LoisCloud_v2"
}

# =========================
#  Routes
# =========================

@app.route("/", methods=["GET"])
def home():
    """Health check simple."""
    return jsonify({
        "status": "ok",
        "engine": "LoisCloud_v2",
        "message": "LoisCloud online 😈"
    })


@app.route("/ask", methods=["POST"])
def ask():
    """
    Body contoh:
    {
      "q": "soalan kau",
      "model": "openai/gpt-4.1-mini"   # optional
    }
    """
    data = request.get_json(silent=True) or {}

    user_msg = data.get("q") or data.get("message") or ""
    model = data.get("model") or "openai/gpt-4.1-mini"

    if not user_msg:
        return jsonify({"error": "Missing 'q' or 'message' field in JSON body"}), 400

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Lois, an API backend assistant for Genesis Lab 2099. "
                    "Jawab secara ringkas, teknikal, dan tolong jangan merapu."
                ),
            },
            {"role": "user", "content": user_msg},
        ],
    }

    try:
        r = requests.post(
            OPENROUTER_URL,
            headers=HEADERS,
            json=payload,
            timeout=30,
        )
    except requests.RequestException as e:
        return jsonify({
            "error": "Request to OpenRouter failed",
            "detail": str(e),
        }), 502

    if r.status_code != 200:
        return jsonify({
            "error": "OpenRouter returned non-200 status",
            "status_code": r.status_code,
            "body": r.text,
        }), 502

    try:
        data = r.json()
        reply = data["choices"][0]["message"]["content"]
    except Exception:
        return jsonify({
            "error": "Invalid response format from OpenRouter",
            "raw": r.text,
        }), 502

    return jsonify({"reply": reply})


# =========================
#  Local dev entrypoint
# =========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
