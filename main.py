from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "engine": "LoisCloud_v2",
        "model": "deepseek/deepseek-r1:free",
        "status": "online"
    })

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        if not data or "q" not in data:
            return jsonify({"error": "Missing 'q' field"}), 400

        prompt = data["q"]

        payload = {
            "model": "deepseek/deepseek-r1:free",
            "messages": [
                {"role": "system", "content": "You are Lois. Respond short, smart and clean."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 256,
            "temperature": 0.7,
        }

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=40
        )

        if response.status_code != 200:
            return jsonify({
                "error": "OpenRouter error",
                "status_code": response.status_code,
                "details": response.text
            }), response.status_code

        result = response.json()
        answer = result["choices"][0]["message"]["content"]

        return jsonify({
            "engine": "deepseek",
            "response": answer
        })

    except Exception as e:
        return jsonify({
            "error": "Server exception",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
