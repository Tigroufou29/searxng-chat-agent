import os
import httpx
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)

# Configuration CORS plus spécifique
CORS(app, 
     origins=["*"],  # Pour testing, en prod spécifiez vos domains
     methods=["POST", "GET", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     supports_credentials=True)

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

@app.route("/chat_api", methods=["POST", "OPTIONS"])
def chat_api():
    # Gérer les pré-requêtes CORS
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
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

    try:
        with httpx.Client(timeout=30) as client:
            r = client.post(MISTRAL_ENDPOINT, headers=headers, json=payload)
            r.raise_for_status()
            reply = r.json()["choices"][0]["message"]["content"]

        return jsonify({"reply": reply})
    
    except Exception as e:
        print(f"Error calling Mistral API: {e}")
        return jsonify({"error": "service_unavailable"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
