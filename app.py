import os
import httpx
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # AJOUT: Import de CORS

app = Flask(__name__)
CORS(app)  # AJOUT: Activation de CORS pour toutes les routes

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_ENDPOINT = "https://api.mistral.ai/v1/chat/completions"
MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")

SYSTEM_PROMPT = (
    "Tu es un agent conversationnel public. "
    "Tu respectes strictement la vie privée : aucune donnée n'est collectée."
)

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/chat_api", methods=["POST"])
def chat_api():
    data = request.get_json(force=True)
    user_msg = data.get("message", "").strip()
    if not user_msg:
        return jsonify({"error": "empty_message"}), 400

    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg}
        ]
    }

    with httpx.Client(timeout=30) as client:
        r = client.post(MISTRAL_ENDPOINT, headers=headers, json=payload)
        r.raise_for_status()
        reply = r.json()["choices"][0]["message"]["content"]

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
