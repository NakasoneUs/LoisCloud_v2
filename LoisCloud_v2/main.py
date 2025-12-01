from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

headers = {
    "Authorization": f"Bearer {OPENROUTER_KEY}",
    "HTTP-Referer": "https://loiscloud",
    "X-Title": "LoisCloud-v2"
}

@app.route("/")
def home():
    return {"status": "LoisCloud online", "engine": "v2"}

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_msg = data.get("q", "")

    payload = {
        "model": "openai/gpt-4.1-mini",
        "messages": [{"role": "user", "content": user_msg}]
    }

    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload
    )

    try:
        reply = r.json()["choices"][0]["message"]["content"]
    except:
        reply = "Error: invalid response."

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
