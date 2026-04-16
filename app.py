import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "groq/compound-mini")

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "ok": True,
        "message": "Backend Groq con web search funcionando"
    })

@app.route("/ask", methods=["POST"])
def ask():
    if not GROQ_API_KEY:
        return jsonify({"error": "Falta configurar GROQ_API_KEY"}), 500

    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()

    if not prompt:
        return jsonify({"error": "La pregunta está vacía"}), 400

    try:
        client = Groq(api_key=GROQ_API_KEY)

        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Responde en español, de forma clara, breve y útil. "
                        "Si la pregunta requiere información actual, nombres dudosos, "
                        "eventos recientes o verificación externa, usa búsqueda web. "
                        "Si hay posible error ortográfico en nombres propios, intenta inferir "
                        "la opción más probable y acláralo con frases como "
                        "'Probablemente te refieres a...'. "
                        "Cuando uses información obtenida en la web, menciona al final "
                        "las fuentes principales en una línea breve."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,
            max_tokens=700
        )

        response_text = completion.choices[0].message.content
        return jsonify({"response": response_text})

    except Exception as e:
        return jsonify({"error": f"Error consultando Groq: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)