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
                        "Responde siempre en español, de forma clara, breve y útil. "
                        "Si la pregunta requiere información actual, verificación externa, "
                        "o trata sobre personas poco conocidas, usa búsqueda web antes de responder. "
                        "No inventes identidades, cargos, biografías, fechas ni datos. "
                        "Si no encuentras evidencia confiable, dilo explícitamente. "
                        "Si el nombre parece tener un error ortográfico, intenta inferir la opción más probable "
                        "basándote en similitud del nombre y en el contexto de la pregunta. "
                        "Prioriza coincidencias plausibles y reconocidas antes que nombres poco respaldados. "
                        "Si hay contexto geográfico o político, úsalo para elegir la alternativa más probable. "
                        "Usa frases como 'Probablemente te refieres a...' o "
                        "'No encontré resultados confiables para ese nombre exacto, pero quizá quisiste decir...'. "
                        "No propongas alternativas arbitrarias o poco sustentadas. "
                        "No afirmes como hecho nada que no esté bien respaldado. "
                        "Si usas información encontrada en la web, menciona al final una línea breve con las fuentes principales."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=700
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