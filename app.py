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
                        "Responde siempre en español, de forma clara, útil y natural. "
                        "Si la pregunta requiere información actual o verificación externa, usa búsqueda web. "
                        "Cuando el usuario pregunte por una persona, intenta recopilar y resumir la información pública más relevante que encuentres. "
                        "Si hay coincidencias razonables, preséntalas de forma útil. "
                        "Si no puedes confirmar totalmente la identidad, no inventes datos, pero sí puedes usar expresiones como "
                        "'probablemente', 'posible coincidencia' o 'encontré información pública asociada a este nombre'. "
                        "No ocultes información útil si encontraste fuentes públicas relevantes. "
                        "Organiza la respuesta en un pequeño resumen y luego agrega una sección breve de fuentes. "
                        "Prioriza ser útil sin afirmar como totalmente seguro algo que no esté plenamente verificado."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=900
        )

        response_text = completion.choices[0].message.content

        return jsonify({
            "response": response_text
        })

    except Exception as e:
        return jsonify({
            "error": f"Error consultando Groq: {str(e)}"
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)