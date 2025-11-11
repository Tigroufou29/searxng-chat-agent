import os
import httpx
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)

# Configuration CORS COMPLÈTE
CORS(app, 
     origins=["https://www.lusk.bzh", "http://localhost:*", "*"],
     methods=["POST", "GET", "OPTIONS", "PUT", "DELETE"],
     allow_headers=["Content-Type", "Authorization", "Accept"],
     expose_headers=["Content-Type", "Authorization"],
     supports_credentials=True,
     max_age=3600)

# Ou pour une solution plus simple pendant le développement :
# CORS(app, resources={r"/chat_api": {"origins": "*"}})

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

# Gestion manuelle des pré-requêtes OPTIONS si nécessaire
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "https://www.lusk.bzh")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Max-Age", "3600")
        return response

@app.route("/chat_api", methods=["POST", "OPTIONS"])
def chat_api():
    # Répondre aux pré-requêtes OPTIONS
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "https://www.lusk.bzh")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response
    
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

        response = jsonify({"reply": reply})
        response.headers.add("Access-Control-Allow-Origin", "https://www.lusk.bzh")
        return response
    
    except Exception as e:
        print(f"Error calling Mistral API: {e}")
        response = jsonify({"error": "service_unavailable"}), 500
        response.headers.add("Access-Control-Allow-Origin", "https://www.lusk.bzh")
        return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
